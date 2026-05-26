# Datalad tutorial repository with ESA/Hubble Pictures of the Week

This is a tutorial data repository to teach the F.A.I.R. Research Data Management (RDM) with [datalad](https://handbook.datalad.org/en/latest/index.html), [git](https://git-scm.com/), and [git-annex](https://git-annex.branchable.com/).


## Prerequisites

You need to install DataLad with a recent version (suggest >= 1.1.0) as well as git, git-annex. Suggested installation methods are via package manager like

    sudo apt install datalad git-annex git-annex-remote-rclone

if possible or via Python in a venv like

    python3 -m pip install datalad

or

    python3 -m pip install --user datalad

or via the uv tool as

    uv tool install datalad

See the [datalad handbook](https://handbook.datalad.org/en/latest/intro/installation.html) for more options.


### Additional tools for this specific example

For this specific example but not for general datalad repositories need `exiftool` and some Python libraries. For the `exiftool` command install via your favorite package manager, e.g. apt with

    sudo apt install libimage-exiftool-perl

(or similar or see [its install instructions](https://exiftool.org/install.html)). For the Python packages pillow and PyExifTool use 

    pip install -r requirements.txt

(or with `pip` or similar).


## Clone the repository

Clone [this repository](https://codebase.helmholtz.cloud/knue/esa-hubble-picture-of-the-week.datalad/project) with datalad via ssh:

    datalad clone git@codebase.helmholtz.cloud:knue/esa-hubble-picture-of-the-week.datalad/project.git

(assuming you have the proper access rights already so you were able to read this).


## Look around

In this data repository consisting of many datasets. You see a directory tree like

    ./
        10__/
            1001/
            1002/
            1003/
        16__/
            1624/
        24__/
            2438/
            2439/
            2440/

... and probably more in the future. This is to organise datasets with a four-digit name `abcd` into sub-dir `ab__/` and inside this into sub-sub-dir `abcd/`. Inside the latter sub-sub-directory all the files that belong to a dataset can be found. This scheme prevents that there will be a very large numbers of sub-dirs in any dir. Even though a local Linux filesystem has no issues with many thousand entires in a directory, at some point it will become problematic, for example with listing them. In parallel HPC file systems this is more critical. Always use some arbitrary approach like this to limit the number of elements in a dir with an upper bound of many hundred or a few thousand.

Inside each dataset directory `ab__/abcd/` you can find several text files and several binary (data) files. The text file `DATASET.json` is a special file, which is the representative file for the entire dataset. It contains the structured metadata for this dataset (see below). It should always be part of a finished dataset. In addition, there is a `README.md` file with some basic information and a preview of the data. This is for convenience for human users to get an overview of the dataset. It is also very handy when looking at the dataset in gitlab.

The binary data files in this example are image files, some of them quite large. They are not the kind of files that are good for handling with git alone. This is what git-annex and datalad are good for and this is part of what this tutorial wants to teach.


## But why are the binary data files broken?

After cloning the repository like above, the binary files `*.jpg` and `*.tif` are listed but not accesible. They are actually broken symlinks. Use `datalad get <subdir>` to get a subset or `datalad get .` to get all of them -- see also [the datalad handbook](https://handbook.datalad.org/en/latest/basics/101-117-sharelocal2.html#where-s-waldo). Datalad will download them for you from their original location on the web (see below). There is another source `s3.casus.science` to download them from but this is not (yet) accessible without additional configuration and authentication information.


## Source of data for this repository

The source of data for our example is ESA/Hubble Picture of the Week [https://esahubble.org/images/potw/](https://esahubble.org/images/potw/).

See [https://esahubble.org/copyright/](https://esahubble.org/copyright/) and the file [LICENSE.md](LICENSE.md).


## Adding more datasets to this repository

The proper way to add more datasets to this data repository is as follows:

1. Point your webbrowser to [https://esahubble.org/images/potw/](https://esahubble.org/images/potw/) and pick one of their pictures of the week which is not yet in this data repository. Go to the specific page like [https://esahubble.org/images/potw2422a/](https://esahubble.org/images/potw2422a/) ... note the 4-digit number near the end of the URL.
2. Create the proper subdirectory for the new data set. If the 4-digit number was `abcd`, then run `mkdir -p ab__/abcd/`, then `cd ab__/abcd/`.
3. Download the web page to the dataset sub-dir, for example `curl -O https://esahubble.org/images/potw2422a/` (in case of issues with older versions of curl use `curl -o potw2422a https://esahubble.org/images/potw2422a/`).
4. Use datalad to download the two images "Fullsize Original" (TIFF format) and "Large JPEG" (JPG format) like `datalad download-url https://esahubble.org/media/archives/images/original/potw2422a.tif https://cdn.esahubble.org/archives/images/large/potw2422a.jpg`
5. Go to the root dir of the data repository again `cd ../../`
6. Now run `./extract_metadata.py ab__/abcd/` to automatically extract all metadataand produce DATASET.json, README.md, and a preview image in PNG format. Only with those extra files the dataset will be complete. (You might need to install the specific dependencies used by the Python script `extract_metadata.py` in this example, either install globally or in a venv or similar.)
7. Run `datalad status` to see what changed in the reporitory. Then run `datalad save -m "<commit message>"` to commit it locally. This is basically the same as `git add` plus `git commit`. Actually, you can use the corresponding git commands just as well.


Now, you have added a new dataset locally to the data collection in this data repository.

Comment 1: In step 3 you might want to use `datalad download-url` instead of `curl` for the HTML file, too. This would be more datalad-ish, of course. For the sake of the example let's pretend that step 3. is an example of producing data yourself in some way whereas step 4. is something that explicitly downloads things from public web links.
Comment 2: For step 6 again, wrapping the call to `extract_metadata.py` in `datalad run` is the even more datalad-ish way.


## Work collaboratively with the data repository

To share your new datasets with the rest of your team, you need to push it to the gitlab repository. This is how you work collaboratively with the data repository.


8. To update your local repository from the central gitlab repository, run `datalad update --how=merge` or the equivalent git command `git pull`. (N.B., `datalad update` by itself is equivalent to `git fetch`). This is how you get new datasets that someone else added.
9. Run `datalad push` or `datalad push --to <name-of-gitlab-sibling>` to bring the gitlab version of this repository up to date. This is equivalent to `git push`.


## The data inventory for the data repository

The gitlab version of this repository is automatically connected to a 
public [dataset inventory](https://data.casus.science/7716/dashboard/#/nc/view/a44a2c02-e0b6-4fa7-ab5e-222f807f5f3a). 
This is where all the metadata of all the datasets (from their DATASET.json files) is collected in a convenient, 
searchable and filterable web browser view. This is where one can search for specific properties resp. the datasets 
that match those properites.

