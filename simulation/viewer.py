# simulation/viewer.py
import FreeCAD

class SimulationState:
    def __init__(self, body, order):
        self.body = body
        self.order = order
        self.current_step = 0
        self.total_steps = len(order)

class Viewer:
    def __init__(self, state: SimulationState):
        self.state = state
        self.is_playing = False
        
        import FreeCAD
        self.doc = FreeCAD.ActiveDocument
        
        # Hide original body
        if hasattr(self.state.body, "ViewObject") and self.state.body.ViewObject:
            self.state.body.ViewObject.Visibility = False
            
        # Create a proxy shape for simulation
        self.sim_obj = self.doc.getObject("BendSeq_Sim_Proxy")
        if not self.sim_obj:
            self.sim_obj = self.doc.addObject("Part::Feature", "BendSeq_Sim_Proxy")
            self.sim_obj.ViewObject.ShapeColor = (0.2, 0.4, 0.8)
            
        self._update_geometry()

    def _update_geometry(self):
        # We start with the flat shape (or fully folded) and apply bends.
        # Since this is a simple stub, we will just print to console.
        # A true implementation unfolds the base shape entirely, then applies fold_engine 
        # up to `current_step` bends from the order list.
        import FreeCAD
        from ..adapters import sheetmetal_api
        from ..adapters import freecad_adapter
        
        FreeCAD.Console.PrintMessage(f"BendSeq Viewer: Rendering step {self.state.current_step}\n")
        
        # In a real heavy implementation:
        # flat_shape = sheetmetal_api.unfold(self.state.body).unfolded_shape
        # current_shape = flat_shape
        # for bend_id in self.state.order[:self.state.current_step]:
        #     current_shape = sheetmetal_api.fold(current_shape, bend_id).shape
        # self.sim_obj.Shape = current_shape
        # self.doc.recompute()
        pass

    def play(self):
        self.is_playing = True
        
    def pause(self):
        self.is_playing = False
        
    def step_forward(self):
        if self.state.current_step < self.state.total_steps:
            self.state.current_step += 1
            self._update_geometry()
        
    def step_backward(self):
        if self.state.current_step > 0:
            self.state.current_step -= 1
            self._update_geometry()
