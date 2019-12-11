"""
Using VTK to visualize obj skull models, and put the images
in a face position. 
"""
import vtk
import argparse
import numpy as np
import random
import utils


class ActorInteractor(vtk.vtkInteractorStyle):
    """This class create a window with a Skull model
    and allow us move it with the keyboard arrows and 
    take a screenshoot of the window. 
    
    Interface
    ----------
    vtk : vtkInteractorStyle
        The class associated to an object in the scenario
    """
    def __init__(self, actor, parent=None, name="principal"):
        if parent is not None:
            self.parent = parent
        else:
            self.parent = vtk.vtkRenderWindowInteractor()

        self.__actor = actor
        self.__name = name
        self.__NUM_ALTERATION = 10

        self.AddObserver("KeyPressEvent", self.keyPressEvent)
        pass

    def __TakeShoot(self, name):
        print("Taking the current status of the windows")
        window_to_image = vtk.vtkWindowToImageFilter()

        # We need to update the render window
        self.parent.GetRenderWindow().Render()

        window_to_image.SetInput(self.parent.GetRenderWindow())
        window_to_image.SetInputBufferTypeToRGBA()
        window_to_image.ReadFrontBufferOff()
        window_to_image.Update()

        writerPNG = vtk.vtkPNGWriter()
        writerPNG.SetFileName("resources/" + name + ".png")
        writerPNG.SetInputConnection(window_to_image.GetOutputPort())
        writerPNG.Write()
        pass

    def keyPressEvent(self, obj, event):
        key = self.parent.GetKeySym()

        if key == 'Up':
            if self.parent.GetShiftKey():
                self.__actor.RotateY(5.0)
            else:
                self.__actor.RotateX(5.0)
        elif key == 'Down':
            if self.parent.GetShiftKey():
                self.__actor.RotateY(-5.0)
            else:
                self.__actor.RotateX(-5.0)
        elif key == 'Right':
            self.__actor.RotateZ(5.0)
        elif key == 'Left':
            self.__actor.RotateZ(-5.0)
        elif key == 'q':
            # Take a shot of the current window
            self.__TakeShoot(self.__name)
            for grades in np.random.uniform(low=-10.0,
                                            high=10.0,
                                            size=(self.__NUM_ALTERATION, )):
                num = random.choice(range(7))

                if num & 0x1:
                    self.__actor.RotateX(grades)
                if num & 0x2:
                    self.__actor.RotateY(grades)
                if num & 0x4:
                    self.__actor.RotateZ(grades)

        self.parent.Render()
        pass

    pass


if __name__ == "__main__":

    parse = argparse.ArgumentParser(
        description=
        "This script shows a 3D skull model. You can interact with this using the computer mouse, the goal is to put the skull in a face position that could be saved in a csv file."
    )
    parse.add_argument("obj",
                       type=str,
                       help="The name of the OBJ file that we must read")

    parse.add_argument("name",
                       type=str,
                       help="The name which the image will be saved",
                       required=False)

    args = parse.parse_args()

    obj_path = utils.givePath(args.obj)
    if args.name is not None:
        name = args.name
    else:
        name = args.obj

    # Create Scenario and Setup obj
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(utils._COLORS_["BLACK"])

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    interactor = vtk.vtkRenderWindowInteractor()

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

    renderer.AddActor(actor)

    # Create the interactor Style, and put it in the interactor windows
    my_interactor = ActorInteractor(actor, interactor, name)
    interactor.SetInteractorStyle(my_interactor)
    interactor.SetRenderWindow(render_window)

    renderer.ResetCamera()

    interactor.Initialize()
    interactor.Start()
    pass
