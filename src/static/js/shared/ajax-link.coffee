define ['jquery'], ($) ->
	class AjaxLink
        constructor: (@url, options) ->
            nullView = {
                setFromJSON: (json) =>
            }
            defaultView = {
                setFromJSON: (json) => 
                    if json
                        alert("#{json.type}: #{json.message}")
            }

            @getView = options.getView or nullView
            @postView = options.postView or defaultView
            @putView = options.putView or defaultView
            @deleteView = options.deleteView or defaultView

        get: (id, dataCallback) =>
            $.ajax
                url: @url
                type: 'GET'
                success: (data) => @_success(@getView, dataCallback)(data)
                complete: (xhr, status) => @_complete(@getView)(xhr, status)

        post: (data, dataCallback) =>
            $.ajax
                url: @url
                type: 'POST'
                data: JSON.stringify(data)
                success: (data) => @_success(@postView, dataCallback)(data)
                complete: (xhr, status) => @_complete(@postView)(xhr, status)

        _success: (view, dataCallback) =>
            return (data) =>
                response = JSON.parse(data)
                if response.data
                    dataCallback(response.data)
                view.setFromJSON(response.status)

        _complete: (view) =>
            return (xhr, status) => 
                if status != 'success'
                    view.setFromJSON({
                        type: xhr.status
                        message: xhr.statusText
                    })