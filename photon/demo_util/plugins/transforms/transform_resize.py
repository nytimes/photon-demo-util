from wand.image import Image

from photon.demo_util.common.transforms import transform_impl


class TransformResize:
    """
    Plugin for resizing an image.

    """

    @transform_impl  # type: ignore
    def run_transform(self, filename: str) -> str:
        """
        Resize an image.

        args:
            filename: The filename.

        returns:
            The name of the completed transform.
        """
        with Image(filename=filename) as img:
            img.transform(resize="750x500>")
            img.save(filename=filename)

        return "resize"
