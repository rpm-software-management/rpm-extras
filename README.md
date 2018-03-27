# rpm-extras

This repository is a collections of scripts and macro files that can not be added to the rpm repository itself. Possible reasons include:

* The code is not stable enough
* It is distribution specific
* Only used by some distributions
* A new feature that is not widely used yet

We encourage distributions to add their own scripts here. It is perfectly fine to have multiple versions of same or similar scripts in the repositories. Please create a sub directory with the name of the distribution in brpscripts/ or macros.d/. The idea is to collect the different implementations and merge them to more general, refined and stable versions. This repository is meant to help with this process. But we are aware that the needs of the distributions differ. It is perfectly fine to end up with multiple variants of the same scripts without an perspective to get them merged. We still hope that for most cases we can settle for one, two or may be three different variants at most.

Although this repository will not follow the release cycle of rpm the content is supposed to be compatible with the current stable release of rpm. We do not collect all versions of the scripts used is some release of each distro. As a general rule of thumb: one version per distribution max. Separate version may be acceptable for down stream (enterprise/long term support) distributions if they differ in the policy they implement.

The idea is that access to this repository is less strict than for the RPM repository. Distributions are encourage to take responsibility for their sub directories throughout the repository. For files shared between distributions it is expected to discuss changes on the rpm-ecosystem mailing list and to create pull requests on Git Hub or send patches for review.
