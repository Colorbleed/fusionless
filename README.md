# fusionless
Python in Black Magic Design's Fusion that sucks less.

Similar to how **Pymel** tries to do Python the right way in Maya this is the same thing for Fusion.

We'll make it *suck less*.

### Supported platforms

**Fusionless** works with Fusion 8.0 (but is compatible since Fusion 6.0+).  
With support for both Python 2 and 3 on all platforms (win/mac/linux).

### Goals

Our highest priority goals are similar to those of **Pymel**:

- Create an open-source python module for Fusion that is intuitive to python users
- Fix bugs and design limitations in Fusion's python module
- Keep code concise and readable
- Add organization through class hierarchy and sub-modules
- Provide documentation accessible via html and the builtin `help() function
- Make it "just work"

Because it should all be that much simpler.  
It's time for that change. Now.

### Installation

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

For more examples see the *[examples](examples)* directory in the repository.

##### PeyeonScript (Fusion pre-8.0 dependency)

To get any access to Fusion (before 8.0) in Python you need PeyeonScript.
As such **fusionless* has this same requirement as it needs to be
able to call the Fusion API.

Unfortunately distribution of it is sparse, so 
[here](http://www.steakunderwater.com/wesuckless/viewtopic.php?t=387)'s a 
topic that has a working download link. All you need is the installer for your 
Python version. Peyeonscript (for 6+) seems to work fine with newer versions of 
Fusion (6.4 or 7+), but is **not** required for Fusion 8+.

