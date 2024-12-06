
Executable can be found in [Releases](https://github.com/sibercat/DBFixResavingPackage/releases) If your going to use .exe the executable was created by [auto-py-to-exe](https://github.com/brentvollebregt/auto-py-to-exe) so you could get a false positive, you know the deal.

===========================================================================
The script is based on [FuncomDBFixGenerator
](https://github.com/VoidEssy/FuncomDBFixGenerator) thanks to the users from Admins United: Conan Discord.

===========================================================================
The script is to fix:
<p>LogPackageName:Warning: String asset reference "None" is in short form, which is unsupported and -- even if valid -- resolving it will be really slow.</p>
<p>LogPackageName:Warning: Please consider resaving package in order to speed-up loading.</p>

Script is looking for pattern  **LogStreaming:Error: Couldn't find file for package (.*?) requested by async loading code.'**

![alt text](https://media.discordapp.net/attachments/1077995857108017344/1314704080311943228/image.png?ex=6754bd16&is=67536b96&hm=40e258eeff0e827270743f6f4d9cd7610a9134ea13e9b144b8cb94b233bde878&=&format=webp&quality=lossless)

===========================================================================
Why is this happening ?
Seems to have started after Funcoms barkeeper hotfix.

In short **Some leftover placable actors remained in the world - after they have been removed or renamed in the mod by the mod author, or mod was removed from the server but placeable actor was placed by a user prior.

In theory server should clean this actors up or skip the search, but seems to be stuck on SearchForPackageOnDisk.
