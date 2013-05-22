define ['jquery', 'ui/control-group', 'bootstrap-datetimepicker'], 
($, ControlGroup, DateTimePicker) ->
    require('bootstrap-datetimepicker')
    class DateTimeInput
        constructor: (@el, options={}) ->
            @el.datetimepicker(options)
            @_picker = @el.data('datetimepicker')
            @required = options.required or false
            @controlGroup = new ControlGroup(options.controlGroup)

        hasInput: =>
            if @el.children('input').val() 
                true
            else 
                false

        getDate: => 
            if @hasInput()
                @_picker.getLocalDate()
            else
                null
        getVal: => 
            if @hasInput()
                Math.round(@getDate().valueOf() / 1000)
            else 
                if @required
                    @controlGroup.setError('Required field.')
                null
        setDate: (date) => @_picker.setDate(date)
        setVal: (val) => @setDate(new Date(val * 1000))
        on: (e, func) => @el.on(e, func)
        show: => @_picker.show()
        hide: => @_picker.hide()
        enable: => @_picker.enable()
        disable: => @_picker.disable()
        setStartDate: (date) => 
            @_picker.startDate = date
            @_picker.update()
        setEndDate: (date) =>
            @_picker.endDate = date
            @_picker.update()