(function() {
  var InformationForm;

  jQuery(function() {
    var informationForm;
    informationForm = new InformationForm();
    return $.ajax({
      url: '/admin/organization-panel/election-panel/information',
      type: 'POST',
      success: function(data) {
        var response;
        response = JSON.parse(data);
        if (response['status'] === 'ERROR') {
          console.log('User not authorized');
          return;
        }
        if (response['election']) {
          console.log(response['election']);
          informationForm.setFromJson(response['election']);
          return informationForm.resetSubmitBtn();
        }
      },
      error: function(data) {
        return console.log('Unknown Error');
      }
    });
  });

  InformationForm = function() {
    var item, picker, self, _i, _j, _k, _len, _len2, _len3, _ref, _ref2, _ref3;
    self = this;
    this.id = "";
    this.name = $('#name');
    this.startDate = $('#startDate');
    this.endDate = $('#endDate');
    this.startTime = $('#startTime');
    this.endTime = $('#endTime');
    this.resultDelay = $('#result-delay');
    this.universal = $('#universal-election');
    this.submitBtn = $('#election-submit');
    $('#startDate, #endDate').parent().datepicker();
    $('#startTime, #endTime').timepicker({
      minuteStep: 5,
      defaultTime: 'current',
      template: 'dropdown'
    });
    this.submitBtn.click(function() {
      var postData;
      if (self.submitBtn.hasClass('disabled')) return false;
      postData = self.toJson();
      if (!postData) return false;
      self.submitBtn.addClass('disabled');
      $.ajax({
        url: '/admin/organization-panel/election-panel/information/update',
        type: 'POST',
        data: {
          'formData': JSON.stringify(postData)
        },
        success: function(data) {
          var response;
          response = JSON.parse(data);
          return self.setSubmitBtn('btn-success', response['msg']);
        },
        error: function(data) {
          return self.setButton('btn-danger', 'Error');
        }
      });
      return true;
    });
    InformationForm.prototype.toJson = function() {
      var json, key, value;
      json = {
        'name': this.getName(),
        'times': this.getTimes(),
        'result_delay': this.getResultDelay(),
        'universal': this.isUniversal()
      };
      for (key in json) {
        value = json[key];
        if (value === null) return null;
      }
      return json;
    };
    InformationForm.prototype.setFromJson = function(json) {
      var delay, end, endDate, endTime, start, startDate, startTime;
      if (!json) return;
      this.id = json['id'];
      this.name.val(json['name']);
      start = new Date(json['times']['start'] + ' UTC');
      end = new Date(json['times']['end'] + ' UTC');
      startDate = formatDate(start);
      startTime = start.toLocaleTimeString();
      endDate = formatDate(end);
      endTime = end.toLocaleTimeString();
      this.startDate.parent().data({
        date: startDate
      });
      this.startDate.parent().datepicker('update');
      this.startDate.val(startDate);
      this.endDate.parent().data({
        date: endDate
      });
      this.endDate.parent().datepicker('update');
      this.endDate.val(endDate);
      this.startTime.timepicker('setTime', startTime);
      this.endTime.timepicker('setTime', endTime);
      delay = json['result_delay'];
      if (!$("#result-delay option[value=" + delay + "]")) {
        this.resultDelay.append("<option id='custom' value='" + delay + "'>" + delay + "</option>");
      }
      this.resultDelay.val(delay).change();
      return this.universal.attr('checked', json['universal'] === true);
    };
    InformationForm.prototype.resetSubmitBtn = function() {
      var text;
      text = 'Create Election';
      if (self.id) text = 'Update Election';
      self.setSubmitBtn('btn-primary', text);
      return self.submitBtn.removeClass('disabled');
    };
    InformationForm.prototype.setSubmitBtn = function(type, text) {
      var disabled;
      if (this.submitBtn.hasClass('disabled')) disabled = true;
      if (disabled) this.submitBtn.addClass('disabled');
      self.restoreDefaultButtonState();
      this.submitBtn.addClass(type);
      return this.submitBtn.text(text);
    };
    InformationForm.prototype.restoreDefaultButtonState = function() {
      this.submitBtn.removeClass('btn-success');
      this.submitBtn.removeClass('btn-error');
      this.submitBtn.removeClass('btn-primary');
      return this.submitBtn.addClass('btn-primary');
    };
    InformationForm.prototype.getName = function() {
      var nameContainer;
      nameContainer = this.name.parent().parent();
      nameContainer.removeClass('error');
      $('.errorMsgName').remove();
      if (!this.name.val()) {
        nameContainer.addClass('error');
        $("<span class='help-inline errorMsgName'>Please enter election " + "name.</span>").insertAfter(this.name);
        return null;
      }
      return this.name.val();
    };
    InformationForm.prototype.getTimes = function() {
      var end, errorMsg, field, start, timeContainer, _i, _len, _ref;
      timeContainer = this.startDate.parent().parent().parent();
      errorMsg = '';
      _ref = [this.startDate, this.startTime, this.endDate, this.endTime];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        field = _ref[_i];
        if (!field.val()) errorMsg = 'Missing information.';
      }
      if (!errorMsg) {
        start = new Date("" + (this.startDate.val()) + " " + (this.startTime.val())).getTime();
        end = new Date("" + (this.endDate.val()) + " " + (this.endTime.val())).getTime();
        start /= 1000;
        end /= 1000;
        if (start > end) errorMsg = 'Start time is later than end time.';
        if (start === end) errorMsg = 'Start time is the same as end time.';
      }
      if (errorMsg) {
        timeContainer.addClass('error');
        $('.errorMsgTime').remove();
        this.startDate.parent().parent().append("<span class='help-inline " + ("errorMsgTime'>" + errorMsg + "</span>"));
        return null;
      } else {
        timeContainer.removeClass('error');
        $('.errorMsgTime').remove();
        return {
          'start': start,
          'end': end
        };
      }
    };
    InformationForm.prototype.getResultDelay = function() {
      return parseInt(this.resultDelay.val());
    };
    InformationForm.prototype.isUniversal = function() {
      return this.universal.attr('checked') === 'checked';
    };
    _ref = [this.name, this.resultDelay, this.universal];
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      item = _ref[_i];
      item.change(this.resetSubmitBtn);
    }
    _ref2 = [this.startTime, this.endTime];
    for (_j = 0, _len2 = _ref2.length; _j < _len2; _j++) {
      picker = _ref2[_j];
      picker.timepicker().on('changeTime.timepicker', this.resetSubmitBtn);
    }
    _ref3 = [this.startDate, this.endDate];
    for (_k = 0, _len3 = _ref3.length; _k < _len3; _k++) {
      picker = _ref3[_k];
      picker.parent().datepicker().on('changeDate', this.resetSubmitBtn);
    }
  };

}).call(this);
