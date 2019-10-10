from wand.image import Image

from photon.demo_util.common.transforms import transform_impl


class TransformSmooth:
    """
    Plugin for smoothing an image with the Kuwahara method.

    """

    @transform_impl  # type: ignore
    def run_transform(self, filename: str) -> str:
        """
        Smoothes an image.

        args:
            filename: The filename.

        returns:
            The name of the completed transform.
        """
        with Image(filename=filename) as img:
            img.kuwahara(radius=2, sigma=1.5)
            img.save(filename=filename)

        return "smooth"
