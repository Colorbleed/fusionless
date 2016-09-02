# fusionless
Python in Black Magic Design's Fusion that sucks less.

Similar to how **Pymel** tries to do Python the right way in Maya this is the same thing for Fusion.  
We'll make it *suck less*.

### Goals

Our highest priority goals are similar to those of **Pymel**:

- Create an open-source python module for Fusion that is intuitive to python users
- Fix bugs and design limitations in Fusion's python module
- Keep code concise and readable
- Add organization through class hierarchy and sub-modules
- Provide documentation accessible via html and the builtin `help() function
- Make it "just work"

Where there's room for a lot more improvement for Fusion outside the above is **scripting documentation**.  
The documentation for scripting in Fusion is pretty much non-existing outside of some forums and video tutorials.  
We need something that is self-explanatory to work with and allows code-completion, but also gets build alongside extensive documentation.

It's time for that change. Now.

### Installation

The **fusionless** package has a dependency on PeyeonScript so ensure you've 
it installed and available to the `PYTHONPATH` as well. (See below for more 
info on PeyeonScript)

To quickly give **fusionless** a spin run this in Fusion (Python):

```python
fusionless_dir = "path/to/fusionless" # <- set the path to fusionless

import sys
sys.path.append('path/to/fusionless')
import fusionless
```

If no errors occured you should be able to use fusionless. For example
add a blur tool to the currently active comp:

```python
import fusionless

current_comp = fusionless.Comp()
current_comp.create_tool("Blur")
```

For more examples see the *examples* directory in the repository.

##### PeyeonScript

It's trivial to install fusionless though there's one cumbersome dependency: 
*PeyeonScript*. 

To get any access to Fusion's scripting in Python you need that package. 
Unfortunately distribution of it is sparse, so [here](http://www.steakunderwater.com/wesuckless/viewtopic.php?t=387)'s a topic that has a 
working download link. All you need is the installer for your Python version.
Peyeonscript (for 6+) seems to work fine with newer versions of Fusion (6.4 or 7+). 
Still need to test under Fusion 8 beta whether it works there as well.

