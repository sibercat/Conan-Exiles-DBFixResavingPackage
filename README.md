
Executable can be found in [Releases](https://github.com/sibercat/DBFixResavingPackage/releases) If your going to use .exe the executable was created by [auto-py-to-exe](https://github.com/brentvollebregt/auto-py-to-exe) so you could get a false positive, you know the deal.

===========================================================================
The script is based on [FuncomDBFixGenerator
](https://github.com/VoidEssy/FuncomDBFixGenerator) thanks to the users from Admins United: Conan Discord.

===========================================================================
The script is to fix:
<p>LogPackageName:Warning: String asset reference "None" is in short form, which is unsupported and -- even if valid -- resolving it will be really slow.</p>
<p>LogPackageName:Warning: Please consider resaving package in order to speed-up loading.</p>

Script is looking for pattern  **LogStreaming:Error: Couldn't find file for package (.*?) requested by async loading code.'**

**Sometimes you would have to run the script one more time after clean***

![alt text](https://github.com/sibercat/Conan-Exiles-DBFixResavingPackage/blob/main/preview_Image.png)

===========================================================================
Why is this happening ?
Seems to have started after Funcoms barkeeper hotfix.

In short **Some leftover placable actors remained in the world - after they have been removed or renamed in the mod by the mod author, or mod was removed from the server but placeable actor was placed by a user prior.

In theory server should clean this actors up or skip the search, but seems to be stuck on SearchForPackageOnDisk.
