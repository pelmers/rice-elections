define ['bootstrap-ui/control-group'], (ControlGroup) ->
	class TextInput
        constructor: (@el, options={}) ->
            @required = options.required or false
            @controlGroup = new ControlGroup(options.controlGroup)

        getValue: =>
            inputString = @el.val().trim()
            if @required and not inputString
                @controlGroup.setError('Required field.')
                return null
            @removeError()
            return inputString

        setValue: (val) =>
            @el.val(val)
            @controlGroup.removeError()