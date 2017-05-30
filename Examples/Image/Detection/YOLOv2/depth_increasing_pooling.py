from cntk import reshape, swapaxes


def transposeAlot(model, permutation):
    nr_of_axes = len(permutation)
    current_permutation = np.arange(nr_of_axes)

    for i in range(nr_of_axes - 1):
        # does this position need to be changed?
        if (permutation[i] != current_permutation[i]):
            # search for current position of the axis to be placed at i!
            for j in range(i, nr_of_axes):
                if (current_permutation[j] == permutation[i]):
                    break

            # swap these two axes
            model = swapaxes(model, i, j)

            tmp = current_permutation[i]
            current_permutation[i] = current_permutation[j]
            current_permutation[j] = tmp
            #print(current_permutation)

    return model


def depth_increasing_pooling(volume, pooling_window_shape, input_shape=None):
    if input_shape is None: input_shape = volume.shape
    # this is necessary in case that the previous model has not yet inferred its shape.
    # In order to perform the reshape properly the input_shape must be known!

    shape_tmp = (input_shape[0],
                 int(input_shape[1] / pooling_window_shape[0]),
                 pooling_window_shape[0],
                 int(input_shape[2] / pooling_window_shape[1]),
                 pooling_window_shape[1])
    final_shape = (input_shape[0] * pooling_window_shape[0] * pooling_window_shape[1],
                   input_shape[1] / pooling_window_shape[0],
                   input_shape[2] / pooling_window_shape[1])

    temp1 = reshape(volume, shape_tmp)

    temp2 = transposeAlot(temp1, (0, 2, 4, 1, 3))

    temp3 = reshape(temp2, final_shape)

    return temp3


if __name__ == '__main__':
    """
    Here the functionality for the pooling_window_shape (2,2) is validated.
    """
    import numpy as np

    def dip_np(volume, pooling_window_shape):
        shape_tmp = (volume.shape[0],
                     int(volume.shape[1] / pooling_window_shape[0]),
                     pooling_window_shape[0],
                     int(volume.shape[2] / pooling_window_shape[1]),
                     pooling_window_shape[1])
        final_shape = (volume.shape[0] * pooling_window_shape[0] * pooling_window_shape[1],
                       int(volume.shape[1] / pooling_window_shape[0]),
                       int(volume.shape[2] / pooling_window_shape[1]))

        volume.shape = shape_tmp
        temp = np.ascontiguousarray(np.transpose(volume, (0, 2, 4, 1, 3)))
        temp.shape = final_shape
        return temp


    def transposeAlotNp(model, permutation):
        nr_of_axes = len(permutation)
        current_permutation = np.arange(nr_of_axes)

        for i in range(nr_of_axes - 1):
            # does this position need to be changed?
            if (permutation[i] != current_permutation[i]):
                # search for current position of the axis to be placed at i!
                for j in range(i, nr_of_axes):
                    if (current_permutation[j] == permutation[i]):
                        break

                # swap these two axes
                model = np.ascontiguousarray(np.swapaxes(model, i, j))

                tmp = current_permutation[i]
                current_permutation[i] = current_permutation[j]
                current_permutation[j] = tmp
                #print(current_permutation)

        return model


    def dip_swap_np(volume, pooling_window_shape):
        shape_tmp = (volume.shape[0],
                     int(volume.shape[1] / pooling_window_shape[0]),
                     pooling_window_shape[0],
                     int(volume.shape[2] / pooling_window_shape[1]),
                     pooling_window_shape[1])
        final_shape = (volume.shape[0] * pooling_window_shape[0] * pooling_window_shape[1],
                       int(volume.shape[1] / pooling_window_shape[0]),
                       int(volume.shape[2] / pooling_window_shape[1]))

        volume.shape = shape_tmp
        temp = transposeAlotNp(volume, (0, 2, 4, 1, 3))
        temp.shape = final_shape
        return temp


    data = np.asarray(
        [[[0, 1, 2, 3],
          [10, 11, 12, 13],
          [20, 21, 22, 23],
          [30, 31, 32, 33]],

         [[100, 101, 102, 103],
          [110, 111, 112, 113],
          [120, 121, 122, 123],
          [130, 131, 132, 133]]
         ], dtype=float)

    print("data:")
    print(data)
    print(data.shape)

    goal = np.asarray(
        [[[0, 2],
          [20, 22]],

         [[1, 3],
          [21, 23]],

         [[10, 12],
          [30, 32]],

         [[11, 13],
          [31, 33]],

         [[100, 102],
          [120, 122]],

         [[101, 103],
          [121, 123]],

         [[110, 112],
          [130, 132]],

         [[111, 113],
          [131, 133]]], dtype=float)

    np_transposed_version = dip_np(np.copy(data), (2, 2))
    print("Succeeded with numpy.transpose:")
    print(np.alltrue(np_transposed_version==goal)) # true
    print()

    np_repeated_swap_version = dip_swap_np(np.copy(data), (2, 2))
    print("Succeeded with selfwritten transpose by numpy.swapaxes:")
    print(np.alltrue(np_repeated_swap_version == goal)) #true
    print()

    cntk_made = depth_increasing_pooling(np.copy(data), (2, 2)).eval()
    print("Succeeded with selfwritten cntk:")
    print(np.alltrue(cntk_made == goal)) #true
    print()

    print("Ouput:")
    print(cntk_made)
    print(cntk_made.shape)
