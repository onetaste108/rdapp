import os


def load(sh_dir, sh_name):
    with open(os.path.join(sh_dir, sh_name)) as f:
        shader = f.read()
    return shader


class Builder:
    def __init__(self, sh_dir):
        self.sh_dir = sh_dir
        self.vert = load(sh_dir, "vert.glsl")
        self.frag_template = load(sh_dir, "frag_template.glsl")
        self.default_config = {
            "RENDER_MODE": "MODE_DEPTH_COLOR",

            "RM_MAX_DEPTH": "10.0",
            "RM_MIN_DEPTH": "0.001",
            "RM_MAX_STEP": "100",
            "RM_STEP_SCALE": "0.05",
            "RM_STOP_DIST": "0.1",
            "AA": "1",

            "SCENE": """
float map(vec3 p) { return 0; };
vec3 display(float depth) { return vec4(0.0, 1.0, 0.0, 1.0); }
            """
        }

    def blit(self):
        frag = """
#version 330
in vec2 v_uv;
uniform sampler2D tex;
out vec4 FragColor;
void main() {
    FragColor = texture(tex, v_uv);
}
        """
        return self.vert, frag

    def live(self, project, live_config):
        config = self.default_config.copy()
        config["RENDER_MODE"] = "MODE_DEPTH_COLOR"
        config["RM_MAX_STEP"] = str(int(live_config.steps))
        config["RM_STEP_SCALE"] = str(float(1/live_config.step_scale))
        config["RM_STOP_DIST"] = str(float(1/live_config.stop_dist))
        config["RM_MAX_DEPTH"] = str(float(live_config.max_depth))
        config["RM_MIN_DEPTH"] = str(float(live_config.min_depth))
        config["SCENE"] = project.code.code
        return self.build(config)

    def depth(self, project, render_config):
        config = self.default_config.copy()
        config["RENDER_MODE"] = "MODE_DEPTH"
        config["RM_MAX_STEP"] = str(int(render_config.steps_max))
        config["RM_STEP_SCALE"] = str(float(1/render_config.step_scale))
        config["RM_STOP_DIST"] = str(float(1/render_config.stop_dist))
        config["RM_MAX_DEPTH"] = str(float(render_config.max_depth))
        config["RM_MIN_DEPTH"] = str(float(render_config.min_depth))
        config["AA"] = str(int(render_config.aa))
        config["SCENE"] = project.code.code
        return self.build(config)

    def color(self, project, render_config):
        config = self.default_config.copy()
        config["RENDER_MODE"] = "MODE_COLOR"
        config["RM_MAX_STEP"] = str(int(render_config.steps_max))
        config["RM_STEP_SCALE"] = str(float(1/render_config.step_scale))
        config["RM_STOP_DIST"] = str(float(1/render_config.stop_dist))
        config["RM_MAX_DEPTH"] = str(float(render_config.max_depth))
        config["RM_MIN_DEPTH"] = str(float(render_config.min_depth))
        config["AA"] = str(int(render_config.aa))
        config["SCENE"] = project.code.code
        return self.build(config)

    def build(self, config):
        frag = self.frag_template
        for key in config:
            frag = frag.replace("@"+key, config[key])

        try:
            os.makedirs("debug", exist_ok=True)
            with open(self.sh_dir+"../debug/frag.glsl", "w") as f:
                f.write(frag)
        except:
            pass

        return self.vert, frag
