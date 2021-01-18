#version 330

in vec2 a_pos;

out vec2 v_pos;
out vec2 v_uv;
out vec2 v_renuv;
out vec2 v_coord;

uniform vec2 patch_pos;
uniform vec2 patch_size;
uniform vec2 render_size;

vec2 fill(vec2 src) {
  float aspect = src.x / src.y;
  if (aspect > 1.0) {
    return vec2(1.0, 1.0 / aspect);
  } else {
    return vec2(1.0 * aspect, 1.0);
  }
}

void main() {
  v_pos = a_pos;
  v_uv = a_pos / 2.0 + 0.5;

  vec2 coord = (v_uv * (patch_size / render_size) + patch_pos / render_size) * 2.0 - 1.0;
  v_renuv = coord;
  v_coord = coord * fill(render_size);

  gl_Position = vec4(a_pos, 0.0, 1.0);
}