shader_type canvas_item;

// THE COMPANION SPLIT FRAME (card frames stage 2, 2026-10-20).
//
// The base game's res://shaders/hsv.gdshader, run twice: once with the
// Colorless frame's numbers (left) and once with the companion's nation tint
// (right), mixed by a smoothstep over the frame's own width. The hsv
// arithmetic is the base shader's, line for line, so the pure-Colorless left
// side is exactly the base Colorless frame.
//
// UV IS AN ATLAS UV. The card frame (card_frame_<type>_s.tres) is an
// AtlasTexture region of ui_atlas_0.png, and a TextureRect drawing an atlas
// region hands the shader the region's coordinates inside the WHOLE atlas,
// not 0..1. `uv_rect` (x, y, width, height, in atlas UV) is that region, set
// per texture by KleeMod.Vfx.CompanionSplitFrame; a plain texture passes
// (0, 0, 1, 1).

uniform float left_h = 1.0;
uniform float left_s = 0.0;
uniform float left_v = 1.2;
uniform float right_h = 1.0;
uniform float right_s = 0.0;
uniform float right_v = 1.2;
uniform float blend_start = 0.4;
uniform float blend_width = 0.2;
uniform vec4 uv_rect = vec4(0.0, 0.0, 1.0, 1.0);

varying vec4 modulate_color;

void vertex() {
    modulate_color = COLOR;
}

vec3 hsv_shift(vec3 rgb, float h, float s, float v) {
    mat3 RGB_to_YIQ = mat3(
        vec3(0.2989,  0.5959,  0.2115),
        vec3(0.5870, -0.2774, -0.5229),
        vec3(0.1140, -0.3216,  0.3114));
    vec3 col = RGB_to_YIQ * rgb;
    float hue = mix(0.0, 6.283185, 1.0 - h);
    float sin_hue = sin(hue);
    float cos_hue = cos(hue);
    mat3 hue_shift = mat3(
        vec3(1.0, 0.0, 0.0),
        vec3(0.0, cos_hue, -sin_hue),
        vec3(0.0, sin_hue, cos_hue));
    col *= hue_shift;
    mat3 sat_shift = mat3(
        vec3(1.0, 0.0, 0.0),
        vec3(0.0, s, 0.0),
        vec3(0.0, 0.0, s));
    col = sat_shift * col;
    col = mix(vec3(0.0), col, v);
    return inverse(RGB_to_YIQ) * col;
}

void fragment() {
    vec4 tex = texture(TEXTURE, UV);
    float x = (UV.x - uv_rect.x) / uv_rect.z;
    float t = smoothstep(blend_start, blend_start + blend_width, x);
    vec3 left = hsv_shift(tex.rgb, left_h, left_s, left_v);
    vec3 right = hsv_shift(tex.rgb, right_h, right_s, right_v);
    COLOR = vec4(mix(left, right, t), tex.a);
    COLOR *= modulate_color;
}
