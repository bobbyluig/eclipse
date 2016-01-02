from skimage.feature import hog
from skimage import data, color, exposure
from skimage import io


image = color.rgb2gray(io.imread('in.jpg'))

fd, hog_image = hog(image, orientations=8, pixels_per_cell=(16, 16),
                    cells_per_block=(1, 1), visualise=True)

hog_image_rescaled = exposure.rescale_intensity(hog_image, in_range=(0, 0.02))

io.imsave('out.jpg', hog_image_rescaled)
