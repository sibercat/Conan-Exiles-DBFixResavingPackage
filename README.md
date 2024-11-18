
Executable can be found in [Releases](https://github.com/sibercat/DBFixResavingPackage/releases) If your going to use .exe the executable was created by [auto-py-to-exe](https://github.com/brentvollebregt/auto-py-to-exe) so you could get a false positive, you know the deal.

===========================================================================
The script is based on [FuncomDBFixGenerator
](https://github.com/VoidEssy/FuncomDBFixGenerator) thanks to the users from Admins United: Conan Discord.

===========================================================================
Basically the script is to fix:
<p>LogPackageName:Warning: String asset reference "None" is in short form, which is unsupported and -- even if valid -- resolving it will be really slow.</p>
<p>LogPackageName:Warning: Please consider resaving package in order to speed-up loading.</p>

Script is looking for pattern  **LogStreaming:Error: Couldn't find file for package (.*?) requested by async loading code.'**

![alt text](https://cdn.discordapp.com/attachments/1077995857108017344/1307945844544376947/image.png?ex=673c26fd&is=673ad57d&hm=fa2ca703ed8236b92f35b73a55c24f1a15d3c1c0ded460727a61337efd54f1d0&)

===========================================================================
Why is this happening ?
Seems to have started after Funcoms barkeeper hotfix.

In short **Some leftover placable actors remained in the world - after they have been removed or renamed in the mod by the mod author, or mod was removed from the server but placable actor was placed by a user prior.

In theory server should clean this actors up or skip the search, but seems to be stuck on SearchForPackageOnDisk.
