define ['jquery', 'ui/control-group'], ($, ControlGroup) ->
    class TextInput
        constructor: (@el, options={}) ->
            @required = options.required or false
            @controlGroup = new ControlGroup(options.controlGroup)
            console.log('Constructing text input')

        getVal: =>
            inputString = @el.val().trim()
            if @required and not inputString
                @controlGroup.setError('Required field.')
                return null
            @controlGroup.removeError()
            return inputString

        setVal: (val) =>
            @controlGroup.removeError()
            @el.val(val)

        change: (func) => @el.change(func)