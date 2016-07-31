<%inherit file="/base.mako" />
<% from logcabin.models import Log %>
<%block name="title">Import from MSPARP - </%block>
<h1>Import from MSPARP</h1>
<div id="content">
  <form action="${request.route_path("upload.msparp", **request.matchdict)}" method="post">
    <p>Save as: <input type="text" name="name" maxlength="${Log.name.type.length}" size="50" required value="${request.matchdict["url"]}"></p>
    % for message in chat_log["messages"][:10]:
    <p style="color: #${message["color"]};">${message["text"]}</p>
    % endfor
    <p>(<a href="${request.registry.settings["urls.msparp"]}/${request.matchdict["url"]}/log" target="_blank">view full chat</a>)</p>
    <p><label><input type="checkbox" name="include_ooc"> Include OOC messages</label></p>
    <p><button>Import</button></p>
  </form>
</div>
