#!/usr/bin/env python

"""
what are separate files and packaging, i dont even
"""

# todo: improve track listing for nonexistant fields

from __future__ import unicode_literals
import os
import json
from urllib import quote
from re import search
from uuid import uuid4

import requests
# from pygments import highlight
# from pygments.lexers import JsonLexer
# from pygments.formatters import HtmlFormatter
from flask import Flask, render_template, request, redirect, url_for, abort
from flask.ext.wtf import Form, StringField, Required


app = Flask(__name__)
app.config.from_object("config")


class ArtistNameForm(Form):
    artist_name = StringField(validators=[Required()])


def get_raw_json(query):
    r = requests.get(query)
    if r.status_code != 200:
        print r.status_code
        abort(404)

    return json.loads(r.content)


def generate_artist_data(name, use_id=False):
    """
    get and return a dictionary with the top hit that we assume is the entry
    for the artist
    """
    if use_id:
        query = "http://54.235.241.196/{0}".format(name)
        artist_json_data = get_raw_json(query)
        return artist_json_data

    query = "http://54.235.241.196/search?t=artist&q={0}&geo=US".format(
        quote(name))
    json_data = get_raw_json(query)
    top_hit_json = json_data["data"][0]

    return top_hit_json


def generate_track_data(id):
    query = "http://54.235.241.196/{0}/tracks".format(id)
    json_data = get_raw_json(query)
    tracks_list = json_data["data"]

    return tracks_list


def generate_similar_artists(id):
    query = "http://54.235.241.196/{0}/similar".format(id)
    json_data = get_raw_json(query)
    similar_artists_list = json_data["data"]

    return similar_artists_list


def generate_mood_json(json_list):
    """
    returns a string in form [hash].json

    {nodes: [{name: "name"}, {name2:"name2}],
    links: [{source: 0, target: 3}]}
    """
    name_nodes = []
    mood_nodes = []

    # get name nodes
    for d in json_list:
        try:
            mood_nodes.append(d["mood"].split(" / "))
            name_nodes.append({"name": d["name"]})
        except KeyError:
            pass

    # assign mood nodes
    # go to every single list in the list and search for one mood at a time

    # get unique keys--flatten list
    unique_moods = \
        frozenset([item for sublist in mood_nodes for item in sublist])
    unique_moods = [{"name": n} for n in unique_moods]

    offset = len(name_nodes)
    nodes = name_nodes + unique_moods

    links = []
    # create links
    # nodes = [{"name": "track"}, {"name": "bleak"}, {"name": "dark"}]
    # name_nodes = [{"name": "track"}]
    # mood_nodes = [["bleak", "dark"]]
    # unique_moods = [{"name": "bleak"}, {"name": "dark"}]
    for base_mood_index, dict_ in enumerate(unique_moods):
        v = dict_["name"]

        for i, single_track_mood_list in enumerate(mood_nodes):
            if v in single_track_mood_list:
                links.append({"source": i, "target": base_mood_index + offset})

    returnable = {"nodes": nodes, "links": links}
    return returnable


def get_mood_json(json_list):
    # generate data
    j = generate_mood_json(json_list)
    uuid = str(uuid4()) + ".json"
    loc = os.path.join(os.getcwd(), "static/json", uuid)

    # save data
    with open(loc, "w") as f:
        json.dump(j, f)

    return uuid


@app.route("/artist/<name>")
def artist_page(name=None):
    """
    generate data, render template
    """
    match = search(r"^artist-\w{8}-\w{4}-\w{4}-\w{4}-\w{12}$", name)

    if match:
        id = name
        artist_data = generate_artist_data(id, use_id=True)
    else:
        artist_data = generate_artist_data(name)
        id = artist_data["id"]

    track_data = generate_track_data(id)
    similarity_data = generate_similar_artists(id)

    return render_template("artist.html",
        data=artist_data, tdata=track_data, sim=similarity_data,
        pygmented={
        # "adata": highlight(str(artist_data), JsonLexer(), HtmlFormatter()),
        # "tdata": highlight(str(track_data), JsonLexer(), HtmlFormatter()),
        #"sdata": highlight(str(similarity_data), JsonLexer(), HtmlFormatter())
        "adata": str(artist_data),
        "tdata": str(track_data),
        "sdata": str(similarity_data)
        },
        json_uuid=url_for("static",
            filename="json/" + get_mood_json(track_data))
    )


@app.route("/", methods=["POST", "GET"])
@app.route("/index.html", methods=["POST", "GET"])
def index():
    form = ArtistNameForm()
    if request.method == "POST":
        if form.validate():
            search_name = request.form["artist_name"]
            return redirect(url_for("artist_page", name=search_name))

    return render_template("index.html", form=form)

if __name__ == "__main__":
    app.debug = False
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    # app.debug = True
    # app.run()
