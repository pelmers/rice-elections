# Place third party dependencies in the shared folder.
# Configuration for require.js to define dependencies for traditional browser
# globals.

requirejs.config(
	"baseUrl": "static/js/shared"
	"paths":
		"app": "../app"
	"shim":
		"bootstrap-datepicker": ["bootstrap"]
		"bootstrap-timepicker": ["bootstrap"]
		"bootstrap-tooltip": ["bootstrap"]
)