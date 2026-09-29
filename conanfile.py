# SPDX-FileCopyrightText: 2024 Howetuft
#
# SPDX-License-Identifier: Apache-2.0

from conan import ConanFile

from conan.tools.cmake import CMakeDeps, CMakeToolchain
from conan.tools.files import save

import os

# Gather here the various dependency versions, for convenience
# (in alphabetic order)
# Pinned to 1.88 for stability: the conan-center boost recipe drops the
# compiled 'system' component starting 1.89 (header-only upstream).
# openvdb/12.1.1's recipe still required 'boost::system' (CI run
# 35422976143); the local openvdb/13.0.0 recipe no longer does, so the
# pin is now conservative rather than forced.
BOOST_VERSION = "1.88.0"
EIGEN_VERSION = "5.0.1"
EMBREE_VERSION = "4.4.1"
FMT_VERSION = "12.2.0"
GLFW_VERSION = "3.4"
IMATH_VERSION = "3.2.2"
IMGUI_VERSION = "1.92.9b"
IMGUIFILEDIALOG_VERSION = "0.6.8"
LIBDEFLATE_VERSION = "1.25"
LIBTIFF_VERSION = "4.7.2"
LLVM_OPENMP_VERSION = "20.1.6"
MINIZIP_VERSION = "4.2.1"
NINJA_VERSION = "1.13.2"
NLOHMANN_JSON_VERSION = "3.12.0"
# NVRTC 13.x emits PTX ISA 9.x that drivers < 591.xx (CUDA 13.0) reject via
# cuModuleLoadDataEx, and its embedded ptxas OOMs on the PathOCL megakernel.
# Keep 12.8.93 until the driver baseline is CUDA 13.1+.
NVRTC_VERSION = "12.8.93"
OCIO_VERSION = "2.5.2"
OIIO_VERSION = "3.1.16.0"
OIDN_VERSION = "2.5.1"
ONETBB_VERSION = "2023.1.0"  # Reminder: do the same in oidn
OPENEXR_VERSION = "3.4.14"
OPENJPH_VERSION = "0.30.1"
OPENSUBDIV_VERSION = "3.7.0"
OPENVDB_VERSION = "13.0.0"
PYBIND11_VERSION = "3.0.1"
SPDLOG_VERSION = "1.17.0"
TSL_ROBIN_MAP_VERSION = "1.4.0"
ZSTD_VERSION = "1.5.7"



class LuxCoreDeps(ConanFile):
    name = "luxcoredeps"
    # Version should be set by `conan install`
    user = "luxcore"
    channel = "luxcore"

    requires = [
        f"openvdb/{OPENVDB_VERSION}",
        f"embree/{EMBREE_VERSION}",
        f"oidn/{OIDN_VERSION}@luxcore/luxcore",
        f"opensubdiv/{OPENSUBDIV_VERSION}",
        f"openjph/{OPENJPH_VERSION}",
        f"openimageio/{OIIO_VERSION}",
        f"imgui/{IMGUI_VERSION}",
        f"glfw/{GLFW_VERSION}",
        f"imguifiledialog/{IMGUIFILEDIALOG_VERSION}@luxcore/luxcore",
    ]

    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        self.requires(
            f"onetbb/{ONETBB_VERSION}",
            override=True,
            libs=True,
            transitive_libs=True,
        )
        self.requires(
            f"libdeflate/{LIBDEFLATE_VERSION}",
            force=True,
            libs=True,
            transitive_libs=True,
        )
        self.requires(
            f"zstd/{ZSTD_VERSION}",
            override=True,
            libs=True,
            transitive_libs=True,
        )
        self.requires(
            f"libtiff/{LIBTIFF_VERSION}",
            override=True,
        )
        self.requires(
            f"opencolorio/{OCIO_VERSION}",
            force=True,
        )
        self.requires(
            f"openexr/{OPENEXR_VERSION}",
            force=True,
        )
        self.requires(
            f"imath/{IMATH_VERSION}",
            override=True,
        )
        self.requires(
            f"minizip-ng/{MINIZIP_VERSION}",
            override=True,
        )
        # Fmt default version (10.x) is not compatible with llvm@20 (MacOS)
        self.requires(
            f"fmt/{FMT_VERSION}",
            force=True,
            transitive_headers=True,
        )

        # Header only deps - make them transitive
        self.requires(
            f"tsl-robin-map/{TSL_ROBIN_MAP_VERSION}",
            transitive_headers=True,
            force=True,
        )
        self.requires(f"eigen/{EIGEN_VERSION}", transitive_headers=True)
        self.requires(
            f"nlohmann_json/{NLOHMANN_JSON_VERSION}",
            transitive_headers=True
        )
        self.requires(f"pybind11/{PYBIND11_VERSION}", transitive_headers=True)
        self.requires(f"spdlog/{SPDLOG_VERSION}", transitive_headers=True)
        self.requires(
            f"boost/{BOOST_VERSION}",
            force=True,
            transitive_headers=True,
        )

        # nvrtc
        if self.settings.os in ("Linux", "Windows"):
            self.requires(f"nvrtc/{NVRTC_VERSION}@luxcore/luxcore")

        # LuxCore build requirements
        # As they are build requirements for LuxCore, they must be full
        # requirements for LuxCoreDeps (otherwise they won't get saved in cache)

        if self.settings.os == "Macos":
            self.requires(
                f"llvm-openmp/{LLVM_OPENMP_VERSION}",
                force=True,
            )


        # Bison/flex (Luxcore build requirement)
        if self.settings.os == "Windows":
            self.requires("winflexbison/[*]", build=False, run=True, visible=True)
        else:
            self.requires("bison/[*]", build=False, run=True, visible=True)
            self.requires("flex/[*]", build=False, run=True, visible=True)

        # Ninja (Luxcore build requirement)
        self.requires("ninja/[*]", build=False, run=True, visible=True)

    def build_requirements(self):
        # LuxCoreDeps build requirements
        self.tool_requires("cmake/[*]")
        self.tool_requires("meson/[*]")
        self.tool_requires("pkgconf/[*]")
        self.tool_requires("yasm/[*]")
        self.tool_requires("m4/[*]")
        self.tool_requires("b2/[*]")

    def generate(self):
        tc = CMakeToolchain(self)

        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            tc.cache_variables["CMAKE_OSX_ARCHITECTURES"] = "arm64"

        tc.generate()

        cd = CMakeDeps(self)
        cd.generate()

    def package(self):
        # Just to ensure package is not empty
        save(self, os.path.join(str(self.package_folder), "dummy.txt"), "Hello World")
