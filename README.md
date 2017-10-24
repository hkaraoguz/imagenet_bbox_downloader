Imagenet BBOX Downloader
========================

This script is for downloading the bounding box (bbox) annotations for a given synset id.

Usage
-----
The script can be used to either download the list of synsets that have bbox annotations or the actual annotations and images of a given synset.

For downloading the synset list run:
```
python main.py --get_synset_list True
```
The result will be written to the `$HOME/imagenet_synset_list.txt`

For downloading the bbox annotations and images for a given `id`, run:
```
python main.py --synset_id id
```
For example, for downloading the annotations of the **monitor** class, run:
```
python main.py --synset_id n03782190
```
The script will first download the annotation data file from Imagenet. Then, it will check for any broken image links and remove them from the initial data.

The remaining xml annotations and images can be found under **Annotations/synset_id/** and **Images/synset_id/** folders respectively.
