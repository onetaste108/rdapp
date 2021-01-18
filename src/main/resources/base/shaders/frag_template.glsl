#version 330

in vec2 v_pos;
in vec2 v_uv;
in vec2 v_renuv;
in vec2 v_coord;

out vec4 FragColor;

uniform vec2 patch_size;

uniform float time;
uniform float sound;
uniform mat4 camera_mat;
uniform sampler2D tex;

uniform sampler2D depth_texture;

uniform bool use_depth_tex;


#define PI 3.1415926535897932384626433832795
#define EPS 0.001

#define RM_MAX_DEPTH @RM_MAX_DEPTH
#define RM_MIN_DEPTH @RM_MIN_DEPTH
#define RM_MAX_STEP @RM_MAX_STEP
#define RM_STEP_SCALE @RM_STEP_SCALE
#define RM_STOP_DIST @RM_STOP_DIST
#define RENDER_MODE @RENDER_MODE
#define AA @AA
#define MODE_DEPTH_COLOR 0
#define MODE_DEPTH 1
#define MODE_COLOR 2

// UTILS

vec2 pack(float x){
  float fix = 255.0/256.0;
  vec2 y = vec2(floor(fract(x*fix*1.0)*255)/255, fract(x*fix*255.0));
  return y;
}

float unpack(vec2 x) {
  float fix = 256.0/255.0;
  return x.x*fix/1.0+x.y*fix/255.0;
}

vec2 ctos(vec3 p) {
  p = normalize(p);
  float phi = atan(p.z, p.x) / PI / 2.0 + 0.5;
  float the = acos(p.y) / PI;
  return vec2(phi, the);
}

vec3 stoc(vec2 uv) {
  vec3 p;
  float phi = (uv.x - 0.5) * PI * 2.0;
  float the = uv.y * PI;
  p.x = sin(the)*cos(phi);
  p.y = cos(the);
  p.z = sin(the)*sin(phi);
  return p;
}

vec2 ctob(vec3 p) {
  float absX = abs(p.x);
  float absY = abs(p.y);
  float absZ = abs(p.z);

  bool isXPositive = p.x > 0;
  bool isYPositive = p.y > 0;
  bool isZPositive = p.z > 0;

  float maxAxis;
  vec2 uv;
  if (isXPositive && absX >= absY && absX >= absZ) {
    maxAxis = absX;
    uv.x = p.z;
    uv.y = p.y;
  }
  if (!isXPositive && absX >= absY && absX >= absZ) {
    maxAxis = absX;
    uv.x = -p.z;
    uv.y = p.y;
  }
  if (isYPositive && absY >= absX && absY >= absZ) {
    maxAxis = absY;
    uv.x = -p.x;
    uv.y = -p.z;
  }
  if (!isYPositive && absY >= absX && absY >= absZ) {
    maxAxis = absY;
    uv.x = -p.x;
    uv.y = p.z;
  }
  if (isZPositive && absZ >= absX && absZ >= absY) {
    maxAxis = absZ;
    uv.x = p.x;
    uv.y = p.y;
  }
  if (!isZPositive && absZ >= absX && absZ >= absY) {
    maxAxis = absZ;
    uv.x = -p.x;
    uv.y = p.y;
  }
  uv.x *= -1;
  uv = 0.5 * (uv / maxAxis + 1.0);
  return uv;
}

vec4 sample(vec2 uv) {
  vec2 uvi = fract(uv/2.0)*2.0;
  if (uvi.x > 1.0) uv.x = (1.0-fract(uv.x));
  else uv.x = fract(uv.x);
  if (uvi.y > 1.0) uv.y = (1.0-fract(uv.y));
  else uv.y = fract(uv.y);
  return texture(tex, (uv-0.5)*0.9+0.5);
}

float rand(float n){return fract(sin(n) * 43758.5453123);}
vec3 rand3(float n){return vec3(rand(n),rand(n+0.333),rand(n+0.666));}
float noise(float p){
	float fl = floor(p);
  float fc = fract(p);
	return mix(rand(fl), rand(fl + 1.0), smoothstep(0.0, 1.0, fc))*2.0-1.0;
}

mat4 rotation3d(vec3 axis, float angle) {
  axis = normalize(axis);
  float s = sin(angle);
  float c = cos(angle);
  float oc = 1.0 - c;
  return mat4(
		oc * axis.x * axis.x + c,           oc * axis.x * axis.y - axis.z * s,  oc * axis.z * axis.x + axis.y * s,  0.0,
    oc * axis.x * axis.y + axis.z * s,  oc * axis.y * axis.y + c,           oc * axis.y * axis.z - axis.x * s,  0.0,
    oc * axis.z * axis.x - axis.y * s,  oc * axis.y * axis.z + axis.x * s,  oc * axis.z * axis.z + c,           0.0,
		0.0,                                0.0,                                0.0,                                1.0
	);
}

vec3 rotate(vec3 a, vec3 c) {
  vec4 b = vec4(a, 1.0);
  b = rotation3d(vec3(1.0, 0.0, 0.0), c.x) * b;
  b = rotation3d(vec3(0.0, 1.0, 0.0), c.y) * b;
  b = rotation3d(vec3(0.0, 0.0, 1.0), c.z) * b;
  return b.xyz;
}



// CAMERA

struct Ray {
  vec3 pos;
  vec3 dir;
};

vec3 raydir(float fov) {
  vec3 forward = vec3(0.0,0.0,1.0);
  vec3 right = vec3(1.0,0.0,0.0);
  vec3 up = vec3(0.0,1.0,0.0);
  vec3 rd = normalize(forward + fov * v_coord.x * right + fov * v_coord.y * up);
  return rd;
}

Ray camPerspective(float fov) {
  Ray cam;
  cam.pos = (camera_mat * vec4(0.0,0.0,0.0,1.0)).xyz;
  cam.dir = (camera_mat * vec4(raydir(fov), 0.0)).xyz;
  return cam;
}

Ray camParallel(float fov) {
  Ray cam;
  cam.pos = (camera_mat * vec4(v_coord*fov, 0.0, 1.0)).xyz;
  cam.dir = (camera_mat * vec4(0.0, 0.0, 1.0, 0.0)).xyz;
  return cam;
}

Ray camVR() {
  Ray cam;
  cam.pos = (camera_mat * vec4(0.0,0.0,0.0,1.0)).xyz;
  cam.dir = (camera_mat * vec4(stoc(v_renuv*0.5+0.5), 0.0)).xyz;
  return cam;
}

Ray camVR3D(float dist) {
  float s = 1.0;
  if (v_renuv.x < 0.0) s = -1.0;
  Ray cam;
  cam.pos = (camera_mat * vec4(0.0,0.0,0.0,1.0)).xyz;
  cam.dir = (camera_mat * vec4(stoc((v_renuv*vec2(2.0,1.0)+vec2(s, 0.0))*0.5+0.5), 0.0)).xyz;
  vec3 ndir = stoc((v_renuv*vec2(2.0,1.0)+vec2(s, 0.0))*0.5+0.5);
  ndir = normalize(vec3(ndir.x, 0.0, ndir.z));
  ndir = vec3(-ndir.z, 0.0, ndir.x);
  ndir = (camera_mat * vec4(ndir, 0.0)).xyz;
  cam.pos += ndir * s * dist / 2.0;
  return cam;
}

// SDF

float sdSphere( vec3 p, float s ) {
  return length(p)-s;
}

float sdBox( vec3 p, vec3 b, float r )
{
  vec3 q = abs(p) - b;
  return length(max(q,0.0)) + min(max(q.x,max(q.y,q.z)),0.0) - r;
}

float sdTorus( vec3 p, vec2 t )
{
  vec2 q = vec2(length(p.xz)-t.x,p.y);
  return length(q)-t.y;
}

float sdCylinder( vec3 p, vec3 c )
{
  return length(p.xz-c.xy)-c.z;
}

float opSmoothUnion( float d1, float d2, float k ) {
    float h = clamp( 0.5 + 0.5*(d2-d1)/k, 0.0, 1.0 );
    return mix( d2, d1, h ) - k*h*(1.0-h); }

float opSmoothSubtraction( float d1, float d2, float k ) {
    float h = clamp( 0.5 - 0.5*(d2+d1)/k, 0.0, 1.0 );
    return mix( d2, -d1, h ) + k*h*(1.0-h); }

float opSmoothIntersection( float d1, float d2, float k ) {
    float h = clamp( 0.5 - 0.5*(d2-d1)/k, 0.0, 1.0 );
    return mix( d2, d1, h ) + k*h*(1.0-h); }

vec3 opMirror(vec3 p, float d) {
  p.x = abs(p.x);
  if (p.x < d) p.x = mix(p.x, 0, smoothstep(0,1,1-p.x/d));
  return p;
}

// DISTORT

vec3 distortSin(vec3 p, float s, float f, vec3 t) {
  p.xyz += 1.000*sin(2.0*(f)*p.yzx+t)*s;
  p.xyz += 0.500*sin(4.0*(f)*p.yzx+t)*s;
  p.xyz += 0.250*sin(8.0*(f)*p.yzx+t)*s;
  p.xyz += 0.050*sin(16.0*(f)*p.yzx+t)*s;
  return p;
}




// SCENE

@SCENE

// -> Ray camera();
// -> float map(vec3 p);
// -> vec4 display(float depth, float dist, vec3 pos, vec3 norm);



// RENDERING

vec3 normal(vec3 p) {
  return normalize(vec3(
      map(vec3(p.x+EPS,p.y,p.z))-map(vec3(p.x-EPS,p.y,p.z)),
      map(vec3(p.x,p.y+EPS,p.z))-map(vec3(p.x,p.y-EPS,p.z)),
      map(vec3(p.x,p.y,p.z+EPS))-map(vec3(p.x,p.y,p.z-EPS))
    ));
}

float raymarch(Ray cam, float depth) {
  float dist;
  for (int i = 0; i < RM_MAX_STEP; i++) {
    dist = map(cam.pos + depth * cam.dir);
    depth += dist * RM_STEP_SCALE;
    if ((dist <= RM_STOP_DIST) || (depth >= RM_MAX_DEPTH)) break;
  }
  // if (dist > RM_STOP_DIST) {
  //   depth = 0.0;
  // }
  return depth;
}


float getDepthTex(vec2 uv) {
  vec4 depthTex = texture(depth_texture, uv);
  float depthBase = unpack(depthTex.xy) * RM_MAX_DEPTH;
  return depthBase;
}

float getDepth() {
  Ray ray = camera();
  float depthBase = RM_MIN_DEPTH;
  if (RENDER_MODE == MODE_DEPTH) {
    if (use_depth_tex) {
      depthBase = getDepthTex(v_uv);
      if (depthBase == 0.0) {
        return 0.0;
      }
    }
  }
  float depth = raymarch(ray, depthBase);
  return depth;
}

vec4 renderDepth() {
  float depth = getDepth();
  vec2 depthPacked = pack(depth/RM_MAX_DEPTH);
  return vec4(depthPacked, 0.0, 1.0);
}

vec4 getColor(float depth) {
  Ray ray = camera();
  vec3 pos = ray.pos + ray.dir * depth;
  float dist = map(pos);
  vec3 norm = normal(pos);
  vec4 color = display(depth, dist, pos, norm);
  return color;
}

vec4 renderColor() {
  float depth;
  vec4 color = vec4(0);
  // vec2 pix = 1.0 / patch_size;
  // vec2 dpix = pix / float(AA);
  // vec2 uv;
  // for (int i = 0; i < AA; i++) {
  //   for (int j = 0; j < AA; j++) {
  //     uv = v_uv - pix/2.0 + dpix/2.0 + dpix*vec2(float(i), float(j));
  //   }
  // }
  depth = getDepthTex(v_uv);
  color += getColor(depth);
  return color;
}

vec4 renderDepthColor() {
  float depth = getDepth();
  vec4 color = getColor(depth);
  return color;
}


void main() {

  vec4 color;
  if (RENDER_MODE == MODE_DEPTH_COLOR) {
    color = renderDepthColor();
  } else if (RENDER_MODE == MODE_DEPTH) {
    color = renderDepth();
  } else if (RENDER_MODE == MODE_COLOR) {
    color = renderColor();
  }

  FragColor = color;
}