(function() {
  var CumulativeVotingPosition, Position, RankedVotingPosition, addPositionModal, all_positions, currentModal, displayPosition, getElectionName, getElectionTimes, getEligibleVoters, getPositions, getResultDelay, isUniversalElection, scrollToTop, submitForm;

  jQuery(function() {
    $('#startDate, #endDate').parent().datepicker();
    $('#startTime, #endTime').timepicker({
      minuteStep: 5
    });
    $('label[rel="tooltip"]').tooltip();
    $('#election-submit').click(submitForm);
    return $('#createForm').bind('reset', function() {
      var all_positions;
      currentModal.resetForm();
      all_positions = [];
      return $('#positions-list').children().remove();
    });
  });

  all_positions = [];

  submitForm = function() {
    var formData, postData, valid;
    if ($('#election-submit').hasClass('disabled')) return false;
    valid = true;
    formData = [getElectionName(), getElectionTimes(), getEligibleVoters(), getPositions(), getResultDelay()];
    $.each(formData, function(index, value) {
      if (!value) return valid = false;
    });
    if (!valid) {
      scrollToTop();
      return false;
    }
    postData = {
      'name': formData[0],
      'start': formData[1]['start'],
      'end': formData[1]['end'],
      'voters': formData[2],
      'positions': formData[3],
      'result_delay': formData[4],
      'universal': isUniversalElection()
    };
    $('#election-submit').addClass('disabled');
    return $.ajax({
      url: '/create-election',
      type: 'POST',
      data: {
        'formData': JSON.stringify(postData)
      },
      success: function(data) {
        var response;
        response = JSON.parse(data);
        scrollToTop();
        $('#server-response').addClass('alert');
        if (response['status'] === 'OK') {
          $('#server-response').addClass('alert-success');
        } else {
          $('#server-response').addClass('alert-error');
        }
        $('#server-response').html(response['msg']);
        return $('#server-response').hide().slideDown(1000);
      }
    });
  };

  scrollToTop = function() {
    return $('html, body').animate({
      scrollTop: $('#createForm').offset().top
    }, 500);
  };

  getElectionName = function() {
    var name, nameContainer;
    name = $('#name');
    nameContainer = name.parent().parent();
    nameContainer.removeClass('error');
    $('.errorMsgName').remove();
    if (!name.val()) {
      nameContainer.addClass('error');
      $("<span class='help-inline errorMsgName'>Please enter election " + "name.</span>").insertAfter(name);
      return null;
    }
    return name.val();
  };

  getElectionTimes = function() {
    var end, endDate, endTime, errorMsg, field, start, startDate, startTime, timeContainer, _i, _len, _ref;
    startDate = $('#startDate');
    startTime = $('#startTime');
    endDate = $('#endDate');
    endTime = $('#endTime');
    timeContainer = startDate.parent().parent().parent();
    errorMsg = '';
    _ref = [startDate, startTime, endDate, endTime];
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      field = _ref[_i];
      if (!field.val()) errorMsg = 'Missing information.';
    }
    if (!errorMsg) {
      start = new Date("" + (startDate.val()) + " " + (startTime.val())).getTime();
      end = new Date("" + (endDate.val()) + " " + (endTime.val())).getTime();
      start /= 1000;
      end /= 1000;
      if (start > end) errorMsg = 'Start time is later than end time.';
      if (start === end) errorMsg = 'Start time is the same as end time.';
    }
    if (errorMsg) {
      timeContainer.addClass('error');
      $('.errorMsgTime').remove();
      startDate.parent().parent().append("<span class='help-inline " + ("errorMsgTime'>" + errorMsg + "</span>"));
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

  getResultDelay = function() {
    return parseInt($('#result-delay').val());
  };

  getEligibleVoters = function() {
    var voter, voters, votersContainer, votersList, _i, _len, _ref;
    voters = $('#eligible-voters');
    votersContainer = voters.parent().parent();
    votersList = [];
    _ref = voters.val().split(',');
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      voter = _ref[_i];
      if (voter.trim()) votersList.push(voter.trim());
    }
    votersContainer.removeClass('error');
    $('.errorMsgEligibleVoters').remove();
    if (votersList.length === 0) {
      votersContainer.addClass('error');
      $("<span class='help-inline errorMsgEligibleVoters'>Missing " + "information.</span>").insertAfter(voters);
      return null;
    }
    return votersList;
  };

  isUniversalElection = function() {
    return $('#universal-election').attr('checked') === 'checked';
  };

  getPositions = function() {
    var pos, posContainer;
    pos = $('#positions-list');
    posContainer = pos.parent().parent();
    posContainer.removeClass('error');
    $('.errorMsgPositions').remove();
    if (all_positions.length === 0) {
      posContainer.addClass('error');
      $("<span class='help-inline errorMsgPositions'>Need at least one " + "position.</span>").insertAfter(pos);
      return null;
    }
    return all_positions;
  };

  displayPosition = function(position) {
    var candidate, html, newPos, _i, _len, _ref;
    html = ("<div style='margin: 5px 0 5px;'><strong>" + position['type'] + ": ") + ("</strong>" + position['name'] + "<br /><ul>");
    _ref = position['candidates'];
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      candidate = _ref[_i];
      html += "<li>" + candidate['name'] + ": " + candidate['netId'] + "</li>";
    }
    if (position['vote_required']) html += "<li><em>Vote required</em></li>";
    if (position['slots']) {
      html += "<li><em>Position slots: " + position['slots'] + "</em></li>";
    }
    if (position['points']) {
      html += "<li><em>Points per voter: " + position['points'] + "</em></li>";
    }
    html += "<li><em>Write-in Slots: " + position['write_in'] + "</em></li>";
    html += "</ul>";
    newPos = $(html);
    $('#positions-list').append(newPos);
    return newPos.hide().slideDown(1000);
  };

  Position = function(type) {
    var self;
    self = this;
    this.type = type;
    this.candidateIDGen = 0;
    this.candidateIDs = [];
    this.candidateIDPrefix = "position-" + this.type + "-candidate-";
    this.addCandidate = $("#position-" + this.type + "-add-candidate");
    this.candidates = $("#position-" + this.type + "-candidates");
    this.name = $("#position-" + this.type + "-name");
    this.writeInSlots = $("#position-" + this.type + "-write-in");
    this.voteRequired = $('#position-required');
    Position.prototype.toJson = function() {
      throw new Error("Not implemented.");
    };
    Position.prototype.reset = function() {
      this.candidateIDs = [];
      this.candidates.children().remove();
      this.name.val('').change();
      return this.voteRequired.attr('checked', false);
    };
    this.addCandidate.click(function() {
      var candidateInput, id, index;
      index = self.candidateIDGen++;
      id = self.candidateIDPrefix + index;
      candidateInput = $('<div/>', {
        "class": 'input-append'
      }).append($('<input>', {
        type: 'text',
        "class": 'input-xlarge, input-margin-right',
        id: "" + id + "-name",
        name: "" + id + "-name",
        width: '200px',
        placeholder: 'Full Name'
      })).append($('<input>', {
        type: 'text',
        "class": 'input-xlarge',
        id: "" + id + "-net-id",
        name: "" + id + "-net-id",
        width: '50px',
        placeholder: 'NetID'
      })).append($('<span/>', {
        "class": 'add-on',
        id: "" + id
      }).append($('<i/>', {
        "class": 'icon-remove'
      })));
      self.candidates.append(candidateInput);
      candidateInput.hide().fadeIn(500);
      self.candidateIDs.push(index);
      return $("#" + id).click(function() {
        var indexPtr;
        indexPtr = self.candidateIDs.indexOf(index);
        if (indexPtr !== -1) self.candidateIDs.splice(indexPtr, 1);
        return $(this).parent().fadeOut(500);
      });
    });
    Position.prototype.getName = function() {
      var nameContainer;
      nameContainer = this.name.parent().parent();
      nameContainer.removeClass('error');
      $('.errorMsgPositionName').remove();
      if (!this.name.val()) {
        nameContainer.addClass('error');
        $('<span class="help-inline errorMsgPositionName">Missing ' + 'information.</span>').insertAfter(this.name);
        return null;
      }
      return this.name.val();
    };
    Position.prototype.getCandidates = function() {
      var can, canList, container, missing, nameInput, netIdInput, _i, _len, _ref;
      missing = false;
      container = this.candidates.parent().parent();
      canList = [];
      _ref = this.candidateIDs;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        can = _ref[_i];
        nameInput = $("#position-" + this.type + "-candidate-" + can + "-name");
        netIdInput = $("#position-" + this.type + "-candidate-" + can + "-net-id");
        if (nameInput.val() === '' || netIdInput.val() === '') {
          missing = true;
        } else {
          canList.push({
            'name': nameInput.val(),
            'netId': netIdInput.val()
          });
        }
      }
      $('.errorMsgCandidateName').remove();
      container.removeClass('error');
      if (missing) {
        container.addClass('error');
        $('<span class="help-inline errorMsgSlots">Number of ' + 'Missing information.</span>').insertAfter(this.candidates);
        return null;
      }
      return canList;
    };
    Position.prototype.getWriteInSlots = function() {
      var max, min, slotsContainer, val;
      slotsContainer = this.writeInSlots.parent().parent();
      val = parseInt(this.writeInSlots.val());
      min = parseInt(this.writeInSlots.attr('min'));
      max = parseInt(this.writeInSlots.attr('max'));
      slotsContainer.removeClass('error');
      $('.errorMsgSlots').remove();
      if (!(min <= val && val <= max)) {
        slotsContainer.addClass('error');
        $('<span class="help-inline errorMsgSlots">Out of valid range.' + '</span>').insertAfter(this.writeInSlots);
        return null;
      }
      return val;
    };
    Position.prototype.hasVoteRequirement = function() {
      return this.voteRequired.attr('checked') === 'checked';
    };
  };

  RankedVotingPosition = function() {
    Position.call(this, "ranked");
    RankedVotingPosition.prototype.toJson = function() {
      var key, position, value;
      position = {
        'type': 'Ranked-Choice',
        'name': this.getName(),
        'candidates': this.getCandidates(),
        'write_in': this.getWriteInSlots(),
        'vote_required': this.hasVoteRequirement()
      };
      for (key in position) {
        value = position[key];
        if (value === null) return null;
      }
      return position;
    };
  };

  RankedVotingPosition.prototype = new Position;

  RankedVotingPosition.prototype.constructor = RankedVotingPosition;

  CumulativeVotingPosition = function() {
    Position.call(this, "cumulative");
    this.points = $('#position-cumulative-points');
    this.slots = $('#position-cumulative-slots');
    CumulativeVotingPosition.prototype.getPoints = function() {
      var max, min, pointsContainer, val;
      pointsContainer = this.points.parent().parent();
      val = parseInt(this.points.val());
      min = parseInt(this.points.attr('min'));
      max = parseInt(this.points.attr('max'));
      pointsContainer.removeClass('error');
      $('.errorMsgSlots').remove();
      if (!(min <= val && val <= max)) {
        pointsContainer.addClass('error');
        $('<span class="help-inline errorMsgSlots">Out of valid range.' + '</span>').insertAfter(this.points);
        return null;
      }
      return val;
    };
    CumulativeVotingPosition.prototype.getSlots = function() {
      var max, min, slotsContainer, val;
      slotsContainer = this.slots.parent().parent();
      val = parseInt(this.slots.val());
      min = parseInt(this.slots.attr('min'));
      max = parseInt(this.slots.attr('max'));
      slotsContainer.removeClass('error');
      $('.errorMsgSlots').remove();
      if (!(min <= val && val <= max)) {
        slotsContainer.addClass('error');
        $('<span class="help-inline errorMsgSlots">Out of valid range.' + '</span>').insertAfter(this.slots);
        return null;
      } else if (val > this.candidateIDs.length && this.getWriteInSlots() < 1) {
        slotsContainer.addClass('error');
        $('<span class="help-inline errorMsgSlots">Number of ' + 'slots exceed number of candidates.</span>').insertAfter(this.slots);
        return null;
      }
      return val;
    };
    CumulativeVotingPosition.prototype.reset = function() {
      Position.prototype.reset.call(this);
      return this.slots.val('1').change();
    };
    CumulativeVotingPosition.prototype.toJson = function() {
      var key, position, value;
      position = {
        'type': 'Cumulative-Voting',
        'name': this.getName(),
        'candidates': this.getCandidates(),
        'write_in': this.getWriteInSlots(),
        'vote_required': this.hasVoteRequirement(),
        'slots': this.getSlots(),
        'points': this.getPoints()
      };
      for (key in position) {
        value = position[key];
        if (value === null) return null;
      }
      return position;
    };
  };

  CumulativeVotingPosition.prototype = new Position;

  CumulativeVotingPosition.prototype.constructor = CumulativeVotingPosition;

  addPositionModal = function() {
    var self,
      _this = this;
    self = this;
    this.selectType = $("#position-select-type");
    this.selectionContent = $(".selection-content");
    this.rankedVotingPosition = new RankedVotingPosition();
    this.cumulativeVotingPosition = new CumulativeVotingPosition();
    this.positionSelected = this.rankedVotingPosition;
    this.addSubmit = $('#position-add-submit');
    addPositionModal.prototype.reset = function() {
      this.selectType.val('0').change();
      this.rankedVotingPosition.reset();
      return this.cumulativeVotingPosition.reset();
    };
    this.selectType.change(function() {
      var selectionId;
      self.selectionContent.hide();
      selectionId = $(this).val();
      $("#" + selectionId).show();
      if (selectionId === '0') {
        return self.positionSelected = self.rankedVotingPosition;
      } else {
        return self.positionSelected = self.cumulativeVotingPosition;
      }
    });
    return this.addSubmit.click(function(e) {
      var position;
      position = _this.positionSelected.toJson();
      if (position === null) return false;
      all_positions.push(position);
      displayPosition(position);
      $('#addPositions').modal('hide');
      return _this.reset();
    });
  };

  currentModal = new addPositionModal();

}).call(this);
