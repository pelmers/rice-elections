// Generated by CoffeeScript 1.6.2
var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

define([], function() {
  var ControlGroup;

  return ControlGroup = (function() {
    function ControlGroup(el) {
      this.el = el != null ? el : null;
      this.removeError = __bind(this.removeError, this);
      this.setError = __bind(this.setError, this);
      null;
    }

    ControlGroup.prototype.setError = function(msg) {
      var error;

      this.removeError();
      if (this.el) {
        this.el.addClass('error');
        error = $('<div>', {
          "class": 'controls help-inline error-msg'
        }).append(msg);
        return this.el.append(error);
      } else {
        return alert("Error: " + msg);
      }
    };

    ControlGroup.prototype.removeError = function() {
      if (this.el) {
        this.el.removeClass('error');
        return this.el.children().filter('.error-msg').remove();
      }
    };

    return ControlGroup;

  })();
});