# Documentation

Extensive documentation exists for this project. The redesigned final CAD package is available in the `cad` folder. Design review documents are located in the `cdr` folder. Mission specifications are located in the `mission` folder. Repair, usage, and tutorial documents are located in the `src` folder. Pre-built HTML files can be used immediately after cloning with Git LFS support. Building the documentation can be done using `pandoc` with the code below.

```bash
pandoc repair.md -o repair.html --template template/template.html --css template/template.css --mathjax --toc --toc-depth 3
pandoc usage.md -o usage.html --template template/template.html --css template/template.css --mathjax --toc --toc-depth 3
pandoc tutorial.md -o tutorial.html --template template/template.html --css template/template.css --mathjax --toc --toc-depth 3 --columns 1000
```
