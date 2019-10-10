from wand.image import Image

from photon.demo_util.common.transforms import transform_impl


class TransformPolaroid:
    """
    Plugin for applying a polaroid effect to an image.

    """

    @transform_impl  # type: ignore
    def run_transform(self, filename: str) -> str:
        """
        Apply a polaroid effect to an image.

        args:
            filename: The filename.

        returns:
            The name of the completed transform.
        """
        with Image(filename=filename) as img:
            img.polaroid()
            img.save(filename=filename)

        return "polaroid"
