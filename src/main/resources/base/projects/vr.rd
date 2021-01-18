{
    "version": [
        0,
        6,
        0
    ],
    "project": {
        "play": true,
        "time": 4010.1327517032623,
        "fps": 60,
        "camera": [
            0.9404270372590078,
            -0.13843771088221488,
            0.31053517666605907,
            -1.5354966845542352e-15,
            -0.30284890461007313,
            0.07404182763356955,
            0.9501580825538203,
            -6.769880720065366e-17,
            -0.15453027680617032,
            -0.9875995058291355,
            0.02770528634022736,
            -9.128581641438476e-16,
            0.20138700648692742,
            3.013181350771974,
            0.2503667798109799,
            1.0000000000000064
        ],
        "texture": "D:\\work\\raduga\\rdapp\\rdapp_v0.6.0\\src\\main\\resources\\base\\default.jpg",
        "audio": "",
        "values": {
            "Random": {
                "_name": "Random",
                "type": "int",
                "ndim": 1,
                "_base": 0,
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
                "_base": 1.2400000000000002,
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
            "Loop": {
                "_name": "Loop",
                "type": "float",
                "ndim": 1,
                "_base": 1000.0,
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
                "_base": 1.0,
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
                "_base": false,
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
                "_base": 1.0,
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
            },
            "d3d": {
                "_name": "d3d",
                "type": "float",
                "ndim": 1,
                "_base": -1.76,
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
            }
        },
        "code": "uniform int Random;\nuniform float Strength;\nuniform float Scale;\nuniform float TimeOffset;\nuniform float Loop;\nuniform float Speed;\nuniform bool Fill;\nuniform float Size;\nuniform float Bump;\nuniform vec3 BumpColor;\nuniform vec2 TexScale;\nuniform vec3 TexRotate;\nuniform float d3d;\n\nRay camera() {\n\treturn camVR3D(d3d);\n}\n\nfloat shape(vec3 p) {\n\tif (!Fill) {\n\treturn sdSphere(p, Size);\n\t} else {\n\t\tvec3 camPos = (camera_mat * vec4(0.0,0.0,0.0,1.0)).xyz;\n\t\tfloat obj = sdSphere(p, Size);\n\t\tfloat back = -sdSphere(p-camPos, length(camPos));\n\t\treturn opSmoothUnion(obj, back, 0.5);\n\t}\n}\n\nvec3 distortion(vec3 p, float s, float f, float t, float sp, float l) {\n\tp += s*1.00*sin((1.0*f*p.yzx+floor(normalize(rand3(Random+0))*sp*l)/l*t+rand3(Random+1))*PI*2);\n\tp += s*0.50*sin((2.0*f*p.yzx+floor(normalize(rand3(Random+2))*sp*l)/l*t+rand3(Random+3))*PI*2);\n\tp += s*0.25*sin((4.0*f*p.yzx+floor(normalize(rand3(Random+4))*sp*l)/l*t+rand3(Random+5))*PI*2);\n\tp += s*0.05*sin((8.0*f*p.yzx+floor(normalize(rand3(Random+6))*sp*l)/l*t+rand3(Random+7))*PI*2);\n\treturn p;\n}\n\nvec3 distort(vec3 p) {\n\treturn distortion(p, Strength, Scale/4.0, time+TimeOffset, Speed/10.0, Loop);\n}\n\nvec4 project(vec3 p) {\n    p = distort(p);\n    p = rotate(p, TexRotate);\n    return sample(ctob(p) * TexScale);\n}\n\nfloat bump(vec3 p) {\n\tif (Bump == 0.0) {\n\t\treturn 0.0;\n\t} else {\n\t\tvec3 color = project(p).rgb * BumpColor;\n\t\treturn (color.x + color.y + color.z) / 3.0 * Bump;\n\t}\n}\n\nfloat map(vec3 p) {\n\tvec3 dp = distort(p);\n    return shape(dp) - bump(p);\n}\n\nvec4 display(float depth, float dist, vec3 pos, vec3 norm) {\n    if (depth == 0.0) {\n        return vec4(0.0);\n    } else {\n        return project(pos);\n    }\n}",
        "script": "\nprint(\"Hello rdapp!\")\n\ndef update(dt):\n\tpass\n        "
    },
    "render_config": {
        "size": [
            1000,
            250
        ],
        "max_patch": 512,
        "steps": 4096,
        "steps_max": 256,
        "step_scale": 10,
        "stop_dist": 100,
        "max_depth": 10,
        "min_depth": 0.001,
        "aa": 2,
        "path": "out/render/",
        "snap_path": "out/snap/",
        "frames": "0",
        "preview_max_size": 1024
    },
    "live_config": {
        "steps": 128,
        "step_scale": 10,
        "stop_dist": 100,
        "max_depth": 10,
        "min_depth": 0.001,
        "size": [
            1410.0,
            589.0
        ],
        "margins": 10,
        "clear": true,
        "downscale": 1
    },
    "app_config": {
        "theme": 70
    }
}