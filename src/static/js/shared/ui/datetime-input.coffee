define ['jquery', 'ui/control-group', 'bootstrap-datetimepicker'], 
($, ControlGroup, DateTimePicker) ->
    require('bootstrap-datetimepicker')
    class DateTimeInput
        constructor: (@el, options={}) ->
            @el.datetimepicker(options)
            @picker = @el.data('datetimepicker')
            @required = options.required or false
            @controlGroup = new ControlGroup(options.controlGroup)
        getDate: => @picker.getDate()
        getVal: => Math.round(@getDate().valueOf() / 1000)
        setDate: (date) => @picker.setDate(date)
        setVal: (val) => @setDate(new Date(val))