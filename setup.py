from setuptools import setup
from setuptools.command.install import install


class PostInstall(install):
	def run(self):
		install.run(self)
		from os import mkdir
		try:
			mkdir("/var/g560")
			mkdir("/var/g560/logs")
		except PermissionError:
			print("_______**********You must create the folder `/var/g560/logs`.**********_______")


with open("README.md", 'r') as f:
	long_description = f.read()


project_name = "g560led"
git_url = f"https://github.com/lwashington3/{project_name}"


setup(
	name=project_name,
	version="0.2.1",
	author="Len Washington III",
	description="LogiTech G560 Linux Controller",
	include_package_data=True,
	long_description=long_description,
	long_description_content_type="test/markdown",
	url=git_url,
	project_urls={
		"Bug Tracker": f"{git_url}/issues"
	},
	license="MIT",
	packages=[project_name],
	install_requires=["pyusb==1.0.2", "colors@git+https://github.com/lwashington3/colors.git"],
	entry_points={
		"console_scripts": [
			f"g560={project_name.replace('-', '_')}.g560:main",
			f"g403={project_name.replace('-', '_')}.g403:main",
			f"g203={project_name.replace('-', '_')}.g203:main",
		]
	},
	classifiers=[
		"Programming Language :: Python :: 3.11"
	],
)
