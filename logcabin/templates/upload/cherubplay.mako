<%inherit file="/base.mako" />
<% from logcabin.models import Log %>
<%block name="title">Import from Cherubplay - </%block>

<h1>Import from Cherubplay</h1>

<form action="${request.route_path("upload.cherubplay", **request.matchdict)}" method="post">
  <p>Save as: <input type="text" name="name" maxlength="${Log.name.type.length}" size="50" required value="${chat_log["chat_user"]["title"] if chat_log["chat_user"] and chat_log["chat_user"]["title"] else chat_log["chat"]["url"]}"></p>
  <p style="color: #${chat_log["messages"][0]["colour"]}; white-space: pre-line;">${chat_log["messages"][0]["text"]}</p>
  <p>(<a href="${request.registry.settings["urls.cherubplay"]}/chats/${chat_log["chat"]["url"]}/" target="_blank">view full chat</a>)</p>
  <p><button>Import</button></p>
</form>
