
#####The task is to create a small Django app, that represents powtoons and permissions web application.

#####Application requirements:

1. The app should have the following models:
    * a. Powtoon - represents a powtoon (video), should have name field, a
    content json field, foreign key to owning user, many to many connection to
    shared-with users.
    * b. User - represents a user.
    * c. Permission - represent a permission.
    * d. Group - a group of permission (many to many connection to a
    Permission).

2. The app should serve the following api functionalities:
    * a. Get a powtoon.
    * b. Create a powtoon.
    * c. Edit a powtoon.
    * . Share a powtoon with other users (meaning add the shared users to the
    powtoons shared-with M2M connection).
    * e. Delete a powtoon.
    * f. Get all powtoons shared with me.

3. Create and load a fixture of the following permission records to the Permission
model:
    * a. Allow to share a powtoon.
    * b. Allow to get a powtoon that is not shared with me and I’m not its owner.
    * 4. Create and load a fixture of the following groups records to the Group model:
    * a. Admin group that holds both permissions mentioned above.

5. Clarifications:
    1. By default, a user is allowed to get only powtoons he owns, or powtoons
    that are shared with him.
    
    2. By default, a user is allowed to edit/delete only powtoons he owns.

Notes:

● You may use built-in Django models.

● You may use any third-party Python/Django library.