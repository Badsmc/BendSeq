# simulation/viewer.py
import FreeCAD

class SimulationState:
    def __init__(self, body, order):
        self.body = body
        self.order = order
        self.current_step = 0
        self.total_steps = len(order)
        self.shapes = [] # [0]=flat, [1]=first bend, ... [n]=fully bent

class Viewer:
    def __init__(self, state: SimulationState):
        self.state = state
        self.is_playing = False
        
        import FreeCAD
        self.doc = FreeCAD.ActiveDocument
        
        if hasattr(self.state.body, "ViewObject") and self.state.body.ViewObject:
            self.state.body.ViewObject.Visibility = False
            
        self.sim_obj = self.doc.getObject("BendSeq_Sim_Proxy")
        if not self.sim_obj:
            self.sim_obj = self.doc.addObject("Part::Feature", "BendSeq_Sim_Proxy")
        
        if hasattr(self.sim_obj, "ViewObject") and self.sim_obj.ViewObject:
            self.sim_obj.ViewObject.ShapeColor = (0.2, 0.4, 0.8)
            
        self._precompute_shapes()
        self._update_geometry()

    def _precompute_shapes(self):
        import FreeCAD
        from ..adapters.freecad_adapter import extract_bends
        from ..core.geometry.bend_simulator import simulate_bend_occ
        from ..core.geometry.transform import compute_force_ids, transform_bend_spec_inplace, clone_spec
        
        FreeCAD.Console.PrintMessage("BendSeq: Precomputing simulation frames...\n")
        all_bends = extract_bends(self.state.body)
        current_specs = {b.id: b for b in all_bends}
        
        current_shape = self.state.body.Shape.copy()
        shapes_backward = [current_shape]
        
        reversed_order = list(reversed(self.state.order))
        
        for bend_id in reversed_order:
            bend = current_specs.get(bend_id)
            if not bend:
                shapes_backward.append(current_shape)
                continue
                
            new_shape, t_info = simulate_bend_occ(
                part_shape=current_shape,
                bend_spec=bend,
                angle_factor=-1.0
            )
            
            if not new_shape or new_shape.isNull():
                new_shape = current_shape
                
            shapes_backward.append(new_shape)
            current_shape = new_shape
            
            next_specs = {}
            force_ids = compute_force_ids(bend, [s for s in current_specs.values() if s.id != bend.id])
            for bid, spec in current_specs.items():
                if bid == bend.id: continue
                cloned = clone_spec(spec)
                if t_info and bid in force_ids:
                    placement = t_info.get("placement")
                    if placement:
                        transform_bend_spec_inplace(cloned, placement)
                next_specs[bid] = cloned
            current_specs = next_specs
            
        self.state.shapes = list(reversed(shapes_backward))

    def _update_geometry(self):
        import FreeCAD
        if not self.state.shapes:
            return
            
        idx = min(self.state.current_step, len(self.state.shapes) - 1)
        self.sim_obj.Shape = self.state.shapes[idx]
        self.doc.recompute()

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
