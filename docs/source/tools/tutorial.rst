Tutorials
============

The object oriented structure of the repository can be daunting at first. To help new users get started, a tutorial notebook has been provided. 
This notebook walks through the basic functionality of the repository, including how to load data, create material objects, and access fits. The tutorial can be found in the `ThermalModelTools` folder of the repository as a Jupyter notebook named `RepositoryTutorial.ipynb`.

This page will also describe some of the basic functions and methods for reference.

.. code-block:: python
    material_of_interest = "Aluminum"
    path_to_mat = os.path.join(<path_to_library>, material_of_interest)
    
    mat_pickle_path = os.path.join(path_to_mat, f"material.pkl")
    with open(mat_pickle_path, "rb") as f:
        mat_obj = pkl.load(f)


.. code-block:: python
    [fit.name for fit in mat_obj.fits]

.. code-block:: console
    ['Aluminum_data', 'Aluminum_1100_data', 'Aluminum_1100_NIST', 'Aluminum_3003F_NIST', ...]

.. code-block:: python
    # Plot the fit
    mat_obj.plot_all_fits()

.. code-block:: python
    # Get thermal conductivity at a specific temperature
    # First, select the fit to use
    fit_to_use = mat_obj.fit_by_name("Aluminum_1100_data")
    T = 50 * u.K
    # Now use the calc_tc method
    k, k_err = fit_to_use.calc_tc(T)

.. code-block:: python
    # Alternatively
    # Load the fit directly from the material object
    fit_to_use = mat_obj.fit_by_name("Aluminum_1100_data")
    # Use the fit function and parameters directly
    k = fit_to_use.function()(T.to(u.K).magnitude, *fit_to_use.parameters)
    # This method might be used if you want to manipulate the output in some way
    # and thus don't want to use the built in (more restrictive) calc_tc method.
