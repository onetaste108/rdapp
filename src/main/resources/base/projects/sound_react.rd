{
    "version": [
        0,
        6,
        0
    ],
    "project": {
        "play": true,
        "time": 257.3027522258039,
        "fps": 24.0,
        "camera": [
            -0.7433936140924977,
            -0.36234153353842047,
            -0.5622051036952191,
            1.027279816088788e-15,
            -0.27999367035068806,
            -0.5947696915294608,
            0.7535599562794103,
            -1.2922173689074215e-16,
            -0.607428622912599,
            0.7176055223693459,
            0.34069463264332756,
            -5.270384074916167e-16,
            3.5686450926289894,
            -4.215934491452126,
            -2.0015810955533646,
            0.9999999999999979
        ],
        "texture": "D:/work/raduga/video_stiched.mp4",
        "audio": "3",
        "values": {
            "Random": {
                "_name": "Random",
                "type": "int",
                "ndim": 1,
                "_base": 245,
                "_track": {
                    "keyframes": [],
                    "viewport": [
                        0,
                        10,
                        1,
                        -1
                    ]
                },
                "_use_track": false
            },
            "Strength": {
                "_name": "Strength",
                "type": "float",
                "ndim": 1,
                "_base": 1.2200000000000002,
                "_track": {
                    "keyframes": [],
                    "viewport": [
                        0,
                        10,
                        1,
                        -1
                    ]
                },
                "_use_track": true
            },
            "Scale": {
                "_name": "Scale",
                "type": "float",
                "ndim": 1,
                "_base": 0.83,
                "_track": {
                    "keyframes": [],
                    "viewport": [
                        0,
                        10,
                        1,
                        -1
                    ]
                },
                "_use_track": true
            },
            "TimeOffset": {
                "_name": "TimeOffset",
                "type": "float",
                "ndim": 1,
                "_base": 694.9806119629241,
                "_track": {
                    "keyframes": [],
                    "viewport": [
                        0,
                        10,
                        1,
                        -1
                    ]
                },
                "_use_track": true
            },
            "Loop": {
                "_name": "Loop",
                "type": "float",
                "ndim": 1,
                "_base": 1000.1999999999998,
                "_track": {
                    "keyframes": [],
                    "viewport": [
                        0,
                        10,
                        1,
                        -1
                    ]
                },
                "_use_track": true
            },
            "Speed": {
                "_name": "Speed",
                "type": "float",
                "ndim": 1,
                "_base": 0.0,
                "_track": {
                    "keyframes": [],
                    "viewport": [
                        0,
                        10,
                        1,
                        -1
                    ]
                },
                "_use_track": true
            },
            "Fill": {
                "_name": "Fill",
                "type": "bool",
                "ndim": 1,
                "_base": true,
                "_track": {
                    "keyframes": [],
                    "viewport": [
                        0,
                        10,
                        1,
                        -1
                    ]
                },
                "_use_track": false
            },
            "Size": {
                "_name": "Size",
                "type": "float",
                "ndim": 1,
                "_base": 2.1799999999999984,
                "_track": {
                    "keyframes": [],
                    "viewport": [
                        0,
                        10,
                        1,
                        -1
                    ]
                },
                "_use_track": true
            },
            "Bump": {
                "_name": "Bump",
                "type": "float",
                "ndim": 1,
                "_base": 0.32000000000000006,
                "_track": {
                    "keyframes": [],
                    "viewport": [
                        0,
                        10,
                        1,
                        -1
                    ]
                },
                "_use_track": true
            },
            "BumpColor": {
                "_name": "BumpColor",
                "type": "float",
                "ndim": 3,
                "_base": [
                    1.0,
                    1.0,
                    1.0
                ],
                "_track": {
                    "keyframes": [],
                    "viewport": [
                        0,
                        10,
                        1,
                        -1
                    ]
                },
                "_use_track": false
            },
            "FOV": {
                "_name": "FOV",
                "type": "float",
                "ndim": 1,
                "_base": 1.0100000000000007,
                "_track": {
                    "keyframes": [],
                    "viewport": [
                        0,
                        10,
                        1,
                        -1
                    ]
                },
                "_use_track": true
            },
            "TexScale": {
                "_name": "TexScale",
                "type": "float",
                "ndim": 2,
                "_base": [
                    1.0,
                    1.0
                ],
                "_track": {
                    "keyframes": [],
                    "viewport": [
                        0,
                        10,
                        1,
                        -1
                    ]
                },
                "_use_track": false
            },
            "TexRotate": {
                "_name": "TexRotate",
                "type": "float",
                "ndim": 3,
                "_base": [
                    0.0,
                    0.0,
                    0.0
                ],
                "_track": {
                    "keyframes": [],
                    "viewport": [
                        0,
                        10,
                        1,
                        -1
                    ]
                },
                "_use_track": false
            }
        },
        "code": "uniform int Random;\nuniform float Strength;\nuniform float Scale;\nuniform float TimeOffset;\nuniform float Loop;\nuniform float Speed;\nuniform bool Fill;\nuniform float Size;\nuniform float Bump;\nuniform vec3 BumpColor;\nuniform float FOV;\nuniform vec2 TexScale;\nuniform vec3 TexRotate;\n\nRay camera() {\n\treturn camPerspective(FOV);\n}\n\nfloat shape(vec3 p) {\n\tif (!Fill) {\n\treturn sdSphere(p, Size);\n\t} else {\n\t\tvec3 camPos = (camera_mat * vec4(0.0,0.0,0.0,1.0)).xyz;\n\t\tfloat obj = sdSphere(p, Size);\n\t\tfloat back = -sdSphere(p-camPos, length(camPos));\n\t\treturn opSmoothUnion(obj, back, 0.5);\n\t}\n}\n\nvec3 distortion(vec3 p, float s, float f, float t, float sp, float l, float toff) {\n\tp += s*1.00*sin((1.0*f*p.yzx+normalize(rand3(Random+0)-0.5)*toff+floor(normalize(rand3(Random+0)-0.5)*sp*l)/l*t+rand3(Random+1))*PI*2);\n\tp += s*0.50*sin((2.0*f*p.yzx+normalize(rand3(Random+2)-0.5)*toff+floor(normalize(rand3(Random+2)-0.5)*sp*l)/l*t+rand3(Random+3))*PI*2);\n\tp += s*0.25*sin((4.0*f*p.yzx+normalize(rand3(Random+4)-0.5)*toff+floor(normalize(rand3(Random+4)-0.5)*sp*l)/l*t+rand3(Random+5))*PI*2);\n\tp += s*0.05*sin((8.0*f*p.yzx+normalize(rand3(Random+6)-0.5)*toff+floor(normalize(rand3(Random+6)-0.5)*sp*l)/l*t+rand3(Random+7))*PI*2);\n\treturn p;\n}\n\nvec3 distort(vec3 p) {\n\treturn distortion(p, Strength, Scale/4.0, time, Speed/10.0, Loop, TimeOffset);\n}\n\nvec4 project(vec3 p) {\n    p = distort(p);\n    p = rotate(p, TexRotate);\n    return sample(ctob(p) * TexScale);\n}\n\nfloat map(vec3 p) {\n\tvec3 dp = distort(p);\n    return shape(dp);\n}\n\nvec4 display(float depth, float dist, vec3 pos, vec3 norm) {\n    if (dist > RM_STOP_DIST && !Fill) {\n        return vec4(0.0);\n    } else {\n        return project(pos);\n    }\n}",
        "script": "print(\"Hello rdapp!\")\nfrom rdapp import noise\ndef update(dt):\n\tapp.get(\"TimeOffset\").value += app.sound*dt*10\n\tapp.cam.orb(*(noise.s3(app.time)*app.sound*dt*100))\n\tpass\n        "
    },
    "render_config": {
        "size": [
            2048,
            2048
        ],
        "max_patch": 512,
        "steps": 4096,
        "steps_max": 256,
        "step_scale": 100.0,
        "stop_dist": 100.0,
        "max_depth": 10,
        "min_depth": 0.001,
        "aa": 2,
        "path": "out/render/",
        "snap_path": "out/snap/",
        "frames": "0",
        "preview_max_size": 1024
    },
    "live_config": {
        "steps": 20,
        "step_scale": 4.0,
        "stop_dist": 5.0,
        "max_depth": 9.659999999999998,
        "min_depth": 1.0,
        "size": [
            1920.0,
            1001.0
        ],
        "margins": 10,
        "clear": true,
        "downscale": 1
    },
    "app_config": {
        "theme": 70
    }
}