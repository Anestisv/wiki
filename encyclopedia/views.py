from django.http import HttpResponseRedirect
from django import forms
from django.urls import reverse
from django.shortcuts import render, redirect

from . import util
import markdown2
import random

# Create a form for new entries
class NewEntryForm(forms.Form):
    newentrytitle = forms.CharField(label = "Enter title here ",
                                    widget = forms.TextInput(attrs = {'autocomplete': 'off'}),
                                    required = " True",)
    newentrytext = forms.CharField(label = "Enter text here ",
                                    widget = forms.Textarea(
                                    attrs = {'rows': 11, "placeholder": "Write your text with Markdown syntax."}),
                                    required = "True")

# create a form for editing entries
class EditEntryForm(forms.Form):
    editentrytitle = forms.CharField(label="Enter title here ",
                                    widget=forms.TextInput(attrs={'autocomplete': 'off'}),
                                    required=" True")
    editentrytext = forms.CharField(label = "Enter text here ",
                                    widget = forms.Textarea(
                                    attrs = {'rows': 11, "placeholder": "Write your text with Markdown syntax."}),
                                    required = "True")

# Displays index page with all the entries
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "heading":"All pages"
    })

# Displays an entry page
def entrypage(request, entry):
    title = entry
    entry = util.get_entry(title)
    if not entry:
        # If entry requested does not exist present an error page
        return render(request, "encyclopedia/notfound.html", {
            "title": title
        })
    else:
        # If the entry does exist, present a page that displays the content of the entry.
        # The title of the page include the name of the entry.
        return render( request, "encyclopedia/entrypage.html", {
            "entry":markdown2.markdown(entry),
            "title": title
        })

# Search queries
def search(request):
    if request.method == "POST":
        sname = request.POST['q']
        entries = util.list_entries()
        matches = []
        # Check if the given query is a substring of each of the existing entries.
        # If so, add the matchung entry to a list (match).
        for entry in entries:
            if sname.lower() in entry.lower():
                matches.append(entry)
        # If the query doesn't match any of the entries redirect to entrypage
        if len(matches) == 0:
            return redirect("entrypage", entry = sname)
        # If there are matches
        # If find an absolute match, present that matche's page
        for i in range(0, len(matches)):
            if sname.lower() == matches[i].lower():
                return redirect("entrypage", entry = matches[i])
        # If not an absolute match, present a list with all possible matches
        return render(request, "encyclopedia/index.html", {
            "entries": matches,
            "heading": "Results found (" + str(len(matches)) + "):"
        })
    else:
        # If get method present the index page
        return HttpResponseRedirect(reverse("index"))

# Create a new entry
def newentry(request):
    if request.method == "POST":
        nef = NewEntryForm(request.POST)
        if nef.is_valid():
            neftitle = nef.cleaned_data['newentrytitle']
            neftext = nef.cleaned_data['newentrytext']
            # If title doesn't exist save the new entry and redirect to that page
            if not util.get_entry(neftitle):
                util.save_entry(neftitle, neftext)
                return redirect("entrypage", entry = neftitle)
            else:
                
                # If title already exists, provide an error message
                entries = util.list_entries()
                for match in entries:
                    if match.lower() == neftitle.lower():
                        neftitle = match
                        error = "The title already exists. Use another title, or edit: "
                        return render(request, "encyclopedia/newentry.html", {
                            "nef": nef,
                            "message": error,
                            "entry": neftitle
                        })
        else:
            nef = NewEntryForm()
            return render(request, "encyclopedia/newentry.html", {"nef": nef})
    else:
        # If get method present an empty form
        nef = NewEntryForm()
        return render(request, "encyclopedia/newentry.html", {
            "nef":nef
        })

# Present a random page of all the entries
def randompage(request):
    entries = util.list_entries()
    rnumber = random.randint(0, len(entries) - 1)
    rname = entries[rnumber]
    return redirect("entrypage", entry = rname)

# Edit an entry
def edit(request):
    if request.method == "POST":
        # Prepopulate the edit form and present for editing
        tokentitle = request.POST['edittitle']
        tokenentry = util.get_entry(tokentitle)
        eef = EditEntryForm(initial={
            'editentrytitle': tokentitle,
            'editentrytext': tokenentry
        })
        return render(request, "encyclopedia/editpage.html", {
            "eef": eef,
            "title": tokentitle
        })
    else:
        # If get method present the index page
        return HttpResponseRedirect(reverse("index"))

# Save an entry you edit
def save(request):
    if request.method == "POST":
        sef = EditEntryForm(request.POST)
        if sef.is_valid():
            savetitle = sef.cleaned_data['editentrytitle']
            savetext = sef.cleaned_data['editentrytext']
            currenttitle = request.POST['hiddentitle']
            # If the changes are on the title
            # If the title remains the same or changed to one that doesn't already exist, save the changes
            if not util.get_entry(savetitle) or currenttitle == savetitle:
                util.save_entry(savetitle, savetext)
                return redirect("entrypage", entry = savetitle)
            else:
                # If the title already exists, don't save and provide an error message
                entries = util.list_entries()
                for match in entries:
                    if match.lower() == savetitle.lower():
                        savetitle = match
                        sef = EditEntryForm(initial={
                                'editentrytitle': currenttitle,
                                'editentrytext': savetext
                            })
                        error = "The title already exists. Use another title, or edit: "
                        return render(request, "encyclopedia/editpage.html", {
                            "eef": sef,
                            "message": error,
                            "entry": savetitle,
                            "title": currenttitle
                        })
        else:
            currenttitle = request.POST['hiddentitle']
            savetitle = sef.cleaned_data['editentrytitle']
            error = "The title already exists. Use another title, or edit: "
            return render(request, "encyclopedia/editpage.html", {
                "eef": sef,
                "message": error,
                "entry": savetitle,
                "title": currenttitle
            })
    else:
        # If get method present the index page
        return HttpResponseRedirect(reverse("index"))