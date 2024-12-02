# ShopAPP5722







## About API















## MongoDB





## Encrypt

#### **基于 Token 的无状态认证**

这种方式不需要在数据库中直接存储登录状态，依赖 Token（如 JWT）进行身份验证。用户登录后，**服务器生成一个 Token**，并返回给客户端，客户端在后续请求中附带该 Token 来证明身份。

#### **实现步骤**

1. **用户登录**：
   1. 用户通过账号密码登录。
   2. 服务器验证账号密码后生成一个 Token（通常包含用户 ID 和过期时间等信息，并用服务器密钥签名）。
   3. 将 Token 返回给客户端。
2. **客户端存储 Token**：
   1. 客户端将 Token 安全地存储（如存储在浏览器的 `localStorage` 或移动设备的安全存储区域）。
3. **每次请求验证**：
   1. 客户端在每次请求中将 Token 作为请求头（`Authorization: Bearer <Token>`）发送给服务器。
   2. **服务器验证 Token 是否有效（检查签名和过期时间）**，从中提取用户信息。

**客户端如何储存token：**

#### **1. 使用 SharedPreferences 存储 Token**

##### **1.1. 使用 EncryptedSharedPreferences**

**EncryptedSharedPreferences** 是 Google 提供的一个更安全的 SharedPreferences 实现，它会自动加密存储的值。

**步骤**：

1. **添加依赖**： 在 `build.gradle` 文件中添加 **EncryptedSharedPreferences** 依赖：

   ```
   gradle
   
   
   Copy code
   dependencies {
       implementation 'androidx.security:security-crypto:1.1.0-alpha03'
   }
   ```

2. **使用 EncryptedSharedPreferences 存储 Token**：

   ```
   kotlin
   
   
   Copy code
   import androidx.security.crypto.EncryptedSharedPreferences
   import androidx.security.crypto.MasterKeys
   
   // 获取加密的 SharedPreferences
   val masterKeyAlias = MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC)
   val sharedPreferences = EncryptedSharedPreferences.create(
       "secure_prefs",
       masterKeyAlias,
       context,
       EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_GCM,
       EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
   )
   
   // 存储 Token
   val editor = sharedPreferences.edit()
   editor.putString("jwt_token", "your_jwt_token_here")
   editor.apply()
   
   // 获取 Token
   val token = sharedPreferences.getString("jwt_token", null)
   if (token != null) {
       // 使用 Token
   }
   ```





#### **2. 使用 Android Keystore 系统（高度安全）**

Android Keystore 系统允许你将敏感数据加密并存储在硬件安全模块（HSM）中。通过使用 **Keystore**，即使设备被 root，数据也很难被破解。

##### **2.1. 使用 Keystore 存储加密的 Token**

1. **生成 Keystore 密钥**：

   ```
   kotlin
   
   
   Copy code
   import android.security.keystore.KeyGenParameterSpec
   import android.security.keystore.KeyProperties
   import javax.crypto.KeyGenerator
   import javax.crypto.SecretKey
   
   fun generateKey(): SecretKey {
       val keyGenSpec = KeyGenParameterSpec.Builder("myKey", KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
           .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
           .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
           .build()
   
       val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
       keyGenerator.init(keyGenSpec)
       return keyGenerator.generateKey()
   }
   ```

2. **加密 Token**：

   ```
   kotlin
   
   
   Copy code
   import javax.crypto.Cipher
   import javax.crypto.KeyGenerator
   import javax.crypto.SecretKey
   import javax.crypto.CipherInputStream
   import android.util.Base64
   
   fun encryptToken(token: String, secretKey: SecretKey): String {
       val cipher = Cipher.getInstance("AES/GCM/NoPadding")
       cipher.init(Cipher.ENCRYPT_MODE, secretKey)
       
       val iv = cipher.iv
       val encryption = cipher.doFinal(token.toByteArray(Charsets.UTF_8))
   
       // Combine IV and ciphertext, and encode as base64 to store
       val ivAndCipherText = iv + encryption
       return Base64.encodeToString(ivAndCipherText, Base64.DEFAULT)
   }
   ```

3. **解密 Token**：

   ```
   kotlin
   
   
   Copy code
   fun decryptToken(encryptedToken: String, secretKey: SecretKey): String {
       val ivAndCipherText = Base64.decode(encryptedToken, Base64.DEFAULT)
       val iv = ivAndCipherText.copyOfRange(0, 12)
       val cipherText = ivAndCipherText.copyOfRange(12, ivAndCipherText.size)
   
       val cipher = Cipher.getInstance("AES/GCM/NoPadding")
       val gcmParameterSpec = GCMParameterSpec(128, iv)  // 128-bit authentication tag
       cipher.init(Cipher.DECRYPT_MODE, secretKey, gcmParameterSpec)
       
       val decryptedToken = cipher.doFinal(cipherText)
       return String(decryptedToken, Charsets.UTF_8)
   }
   ```

> **注意**：这将是最安全的存储方式，Token 是加密存储在设备的硬件中，无法被直接提取，即使设备被 root 或者文件系统被访问。