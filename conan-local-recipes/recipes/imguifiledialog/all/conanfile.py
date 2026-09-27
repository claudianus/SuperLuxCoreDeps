# SPDX-FileCopyrightText: 2024 Howetuft
#
# SPDX-License-Identifier: Apache-2.0

from conan import ConanFile

from conan.tools.cmake import CMakeDeps, CMakeToolchain, cmake_layout, CMake
from conan.tools.files import save
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, load, rmdir, rm
import os

class ImguiFileDialogConan(ConanFile):
    name = "imguifiledialog"
    user = "luxcore"
    channel = "luxcore"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    homepage = "https://github.com/aiekick/ImGuiFileDialog"
    license = "MIT"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_std_filesystem": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "use_std_filesystem": True,
    }
    requires = "imgui/1.92.9b"  # Must be same version as in main conanfile.py


    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        save(
            self,
            path=os.path.join(self.source_folder, "CMakeLists.txt"),
            content=(
                # Leading newline: upstream 0.6.8 CMakeLists.txt has no
                # trailing newline, so a plain append glues find_package
                # onto the last upstream line and CMake fails to parse.
                "\n"
                "find_package(imgui)\n"
                "target_link_libraries(ImGuiFileDialog PRIVATE imgui::imgui)\n"
                "install(TARGETS ImGuiFileDialog)\n"
                "install(FILES ImGuiFileDialog.h ImGuiFileDialogConfig.h DESTINATION include)\n"
            ),
            append=True,
        )  # Append


    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        if self.options.use_std_filesystem:
            tc.preprocessor_definitions["USE_STD_FILESYSTEM"] = None
        if self.settings.os == "Windows":
            # The global BUILD_SHARED_LIBS=ON makes this a DLL with zero
            # exported symbols — MSVC emits no import .lib, so the packaged
            # cpp_info.libs entry cannot be satisfied. Keep it static.
            tc.variables["BUILD_SHARED_LIBS"] = False
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["ImGuiFileDialog"]
