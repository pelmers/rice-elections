define ['jquery', 'ui/datetime-input'], ($, DateTimeInput) ->
	class DateTimeRangeInput
        ###
            An input that allows a user to specify a datetime range.

            Args:
                startEl: the start datetime element
                endEl: the end datetime element
                options: the options object, delegated to DateTimeInput
                    required: whether input is required
                    language: language string e.g. 'en'
                    pickTime: whether the user can pick time
                    pick12HourFormat: whether the user can pick 12 hour format
                    pickSeconds: whether user can pick seconds
                    required: whether input is required
                    pastAllowed: whether past input is allowed
                    controlGroup: the control group element
        ###
        constructor: (@startEl, @endEl, options) ->
            @required = options.required            
            @pastAllowed = options.pastAllowed
            if not @pastAllowed
                options.startDate = new Date()

            @_startDt = new DateTimeInput($(@startEl), options)
            @_endDt = new DateTimeInput($(@endEl), options)

            @_startDt.on 'changeDate', (e) => @_validate_range()
            @_endDt.on 'changeDate', (e) => @_validate_range()

        _validate_range: =>
            valid = true

            if @_startDt.hasInput()
                if not @pastAllowed and @_startDt.getDate() < new Date()
                    @_startDt.controlGroup.setError(
                        'Start time cannot be in the past.')
                    valid = false

            if @_startDt.hasInput() and @_endDt.hasInput()
                if @_endDt.getDate() < @_startDt.getDate()
                    @_endDt.controlGroup.setError(
                        'End time is before start time.')
                    valid = false

            if valid
                @_startDt.controlGroup.removeError()
                @_endDt.controlGroup.removeError()

            return valid

        hasInput: => @_startDt.hasInput() and @_endDt.hasInput()

        toJSON: =>
            if @hasInput()
                if @_validate_range()
                    start: @_startDt.getVal(), end: @_endDt.getVal()
                else
                    null
            else
                if @required
                    @_startDt.controlGroup.setError('Required input.')
                null

        setFromJSON: (vals) =>
            @_startDt.setVal(vals.start)
            @_endDt.setVal(vals.end)
            @_validate_range()

        disableStart: => @_startDt.disable()
        disableEnd: => @_endDt.disable()
        enableStart: => @_startDt.enable()
        enableEnd: => @_endDt.enable()
        on: (e, func) => 
            @_startDt.el.on(e, func)
            @_endDt.el.on(e, func)


