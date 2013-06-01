# Place third party dependencies in the shared folder.
# Configuration for require.js to define dependencies for traditional browser
# globals.

requirejs.config(
  "baseUrl": "/static/js/shared"
  "paths":
    "app": "/static/js"
  "shim":
    "bootstrap-datepicker":
      deps: ["bootstrap"]
      exports: "jQuery.fn.datepicker"
    "bootstrap-datetimepicker": ["bootstrap"]
    "bootstrap-timepicker": ["bootstrap"]
    "bootstrap-tooltip": ["bootstrap"]
    "bootstrap": ["jquery"]
)
