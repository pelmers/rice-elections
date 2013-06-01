define ['jquery'], ($) ->
	class ControlGroup
		constructor: (@el=null) -> null

        ###
            Set error.
            Args:
                msg {String}: error message string.
        ###
        setError: (msg) =>
            @removeError()
            if @el
                @el.addClass('error')
                error = $(
                    '<div>',
                        class: 'controls help-inline error-msg'
                    ).append(msg)
                @el.append(error)
            else
                alert("Error: #{msg}")

        ###
            Remove error.
        ###
        removeError: =>
            if @el
                @el.removeClass('error')
                @el.children().filter('.error-msg').remove()