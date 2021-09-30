#version 330
in layout(location = 0) vec3 position;
in layout(location = 1) vec2 inTexCoords;

uniform mat4 scale;
uniform mat4 view;
uniform mat4 projection;
uniform mat4 model;

out vec2 outTexCoords;

void main()
{
    gl_Position = projection * view * model * scale * vec4(position,1.0f);
    //gl_Position = transform * vec4(position,1.0f);
    outTexCoords = inTexCoords;
}
