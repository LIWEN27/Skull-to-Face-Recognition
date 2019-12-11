import cv2
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk
import argparse
import utils


def ImageToNumpy(render_window, render):
    """This function takes a screenshot of the actual render windows and transforms it in a Numpy matrix that could be handled in other contexts
    
    Parameters
    ----------
    render_window : vtkRenderWindow
        The renderer of the program
    
    Returns
    -------
    Numpy Multidimensional array
        The image interpreted as a numpy matrix of row x col x 3
    """
    render_window.Render()
    render.ResetCamera()
    render_window.Render()

    wind_to_image = vtk.vtkWindowToImageFilter()
    wind_to_image.SetInput(render_window)
    wind_to_image.SetInputBufferTypeToRGBA()
    wind_to_image.ReadFrontBufferOff()
    wind_to_image.Update()

    image = wind_to_image.GetOutput()
    row, col, _ = image.GetDimensions()
    sc = image.GetPointData().GetScalars()

    result = vtk_to_numpy(sc)
    result = result.reshape(row, col, -1)

    return result


def TakeShotOfObj(obj_path, transform_matrix=None):
    # Create Scenario and Setup obj
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(utils._COLORS_["BLACK"])

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    # Create the camera
    camera = vtk.vtkCamera()
    camera.SetViewUp(0, 0, -1)
    camera.SetPosition(0, -1, 0)
    camera.SetFocalPoint(0, 0, 0)
    camera.ComputeViewPlaneNormal()
    camera.Azimuth(30.0)
    camera.Elevation(30.0)

    # Attaching the camera at the scene
    renderer.SetActiveCamera(camera)
    renderer.ResetCamera()

    # Read the object and put this in the scene
    reader = vtk.vtkOBJReader()
    reader.SetFileName(obj_path)
    reader.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(utils._COLORS_["WHITE"])

    if transform_matrix is not None:
        matrix = vtk.vtkMatrix4x4()

        for num, elem in enumerate(transform_matrix.ravel()):
            matrix.SetElement(num % 4, int(num / 4), elem)

        actor.SetUserMatrix(matrix)

    renderer.AddActor(actor)

    return ImageToNumpy(render_window, renderer)


if __name__ == "__main__":
    parse = argparse.ArgumentParser(
        description=
        "This script takes a 3D skull model and compare it with the principal skull that we saved finding a homography between them."
    )
    parse.add_argument("obj",
                       type=str,
                       help="The name of the OBJ file that we must compare")

    args = parse.parse_args()

    obj_path = utils.givePath(args.obj)

    principal_image = cv2.imread("resources/principal.png",
                                 cv2.IMREAD_GRAYSCALE)
    model_image = cv2.cvtColor(TakeShotOfObj(obj_path), cv2.COLOR_RGB2GRAY)

    # Detect ORB features and compute descriptors.
    orb = cv2.ORB_create(500)
    keypoints1, descriptors1 = orb.detectAndCompute(principal_image, None)
    keypoints2, descriptors2 = orb.detectAndCompute(model_image, None)

    # Match features.
    matcher = cv2.DescriptorMatcher_create(
        cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(descriptors1, descriptors2, None)

    # Sort matches by score
    matches.sort(key=lambda x: x.distance, reverse=False)

    # Remove not so good matches
    numGoodMatches = int(len(matches) * 0.15)
    matches = matches[:numGoodMatches]

    # Extract location of good matches
    points1 = np.zeros((len(matches), 2), dtype=np.float32)
    points2 = np.zeros((len(matches), 2), dtype=np.float32)

    for i, match in enumerate(matches):
        points1[i, :] = keypoints1[match.queryIdx].pt
        points2[i, :] = keypoints2[match.trainIdx].pt

    # Find homography
    h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)

    H_mat = np.zeros((4, 4), dtype=np.float)
    H_mat[:3, :3] = h
    H_mat[3, 2] = 1

    print("The transformation matrix is:\n{}\nThe mask is:\n{}".format(
        H_mat, mask))

    cv2.imshow("Proof of concept", TakeShotOfObj(obj_path, H_mat))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
