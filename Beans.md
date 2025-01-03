# Theory (Why)

What is dependency injection? It's simply a way of writing/architecting OOP applications to make them more configurable and easy to test. At a high level, it makes it so we can easily swap out different chunks of code for different situations. But applying dependency injection to our application means having to slightly restructure how we construct some classes in our application. 
## Definition 

The definition of dependency injection is simply this: If we have a Class X that relies on code from Class Y to work, then instead of having X create an instance of Y, an instance of Y should be passed in as a parameter to X instead. 

Example **WITHOUT** dependency injection:
```java
public class UserRepository {

    private final DatabaseConnection db;

    // BAD: WITHOUT DEPENDENCY INJECTION
    public UserRepository() {
        this.db = new DatabaseConnection("jdbc://localhost:3000/postgres");
    }

    public getAllUsers() {
        return this.db.fetch("SELECT * FROM USERS;");
    }
}
```

Example **WITH** dependency injection:
```java
public class UserRepository {

    private final DatabaseConnection db;

    // GOOD: WITH DEPENDENCY INJECTION
    public UserRepository(DatabaseConnection db) {
        this.db = db;
    }

    public getAllUsers() {
        return this.db.fetch("SELECT * FROM USERS;");
    }
}
```
## Benefits

At first it might not seem clear what the benefits of such a simple change are. But basically, it makes it so that you can easily swap in different instances of objects depending what environment your app is running. The 2 most common scenarios are:

1. Passing in different objects depending on if we're in dev vs prod. For example, in the UserRepository code above, the first database object is hardcoded so there's no way to change to a dev server. When dependency injection is introduced, we then have the flexibility to pass in different databases objects depending on if we're in dev vs prod.
2. Passing in mock objects when unit testing. Having all dependencies parameterized gives us the ability to pass in mock objects so we can isolate testing to only the class we want to test and not its dependencies.
   
   Example:
   
```java
// Example class we want to unit test. 
// We show how introducing dependency injection into BankService makes it easier to test.
public class BankService {

    private final BankDb bankDb;

    public BankService(BankDb bankDb) {
        this.bankDb = bankDb;
    }

    /**
     * Transfers money between two accounts if the source has sufficient funds.
     * Returns true if successful, false if insufficient funds.
     */
    public boolean transfer(String fromAccount, String toAccount, double amount) {
        double fromBalance = bankDb.getBalance(fromAccount);
        if (fromBalance < amount) {
            return false;
        }

        double toBalance = bankDb.getBalance(toAccount);

        // Update balances in the database
        bankDb.updateBalance(fromAccount, fromBalance - amount);
        bankDb.updateBalance(toAccount, toBalance + amount);
        return true;
    }
}

// The Unit Test
public class BankServiceTest {

    @Test
    public void testSuccessfulTransfer() {
        BankDb mockDb = Mockito.mock(BankDb.class);
        when(mockDb.getBalance("X")).thenReturn(100.0);
        when(mockDb.getBalance("Y")).thenReturn(50.0);

        // Inject mocked DB.
        BankService service = new BankService(mockDb);

        // Execute the transfer
        boolean result = service.transfer("X", "Y", 40.0);

		// Verify
        assertTrue(result);
        verify(mockDb).updateBalance("X", 60.0);
        verify(mockDb).updateBalance("Y", 90.0);
    }

    @Test
    public void testInsufficientFunds() {
        BankDb mockDb = Mockito.mock(BankDb.class);
        when(mockDb.getBalance("X")).thenReturn(20.0);
        when(mockDb.getBalance("Y")).thenReturn(50.0);

        BankService service = new BankService(mockDb);

        // Attempt to transfer 40.0, which should fail
        boolean result = service.transfer("X", "Y", 40.0);
        
        // Verify that balances were NOT updated because the transfer failed
        assertFalse(result);
        verify(mockDb, never()).updateBalance(anyString(), anyDouble());
    }
}
```
## Downsides

It should be noted that dependency injection does incur some downsides. 
1. It makes constructing your application harder which requires the introduction of frameworks like Spring (This is discussed in more detail in later sections)
2. Dependency injection can make your app more configurable, but overuse of the pattern can lead to unnecessary indirection and complexity
3. Worse debuggability. What would have been normal compile-time errors now become complex autowire runtime errors with long stack traces.
## Manual Dependency Injection

In the previous section, we explained the theory/motivation behind dependency injection and why it sometimes makes sense to inject dependencies. The problem is that if we parameterize an object to use dependency injection, now creating that object is harder because there's an extra step of making sure the right dependencies are passed in. Example:

```java
// Creating a UserRepository class that doesn't use dependency injection is easier.
UserRepository userRepository = new UserRepository();

// When dependency injection is introduced, there's now the extra step of having 
// to create a database object and then pass it into the UserRepository constructor
DataSource dataSource = new DatabaseConnection("jdbc://localhost:3000/postgres");
UserRepository userRepository = new UserRepository(dataSource);
```

The above example might not seem so bad, but when you start working with applications that have hundreds of objects, constructing the entire object graph for your application can become very tedious. Introducing dependency injection into your applications means having to resolve all the dependencies of your application by hand and constructing the object graph for your application at the start of your app (Usually the main method). 

Here's a more complex example of manual dependency injection involving an app with 5 objects (DataSource, UserRepository, EmailService, UserRepository, UserController):

```java
// ======== Dependencies ========

class DataSource {
    private final String connectionString;

    public DataSource(String connectionString) {
        this.connectionString = connectionString;
    }

    public String getConnectionString() {
        return connectionString;
    }
}

class UserRepository {
    private final DataSource dataSource;

    public UserRepository(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    public String findUserById(String userId) {
        // In a real scenario, you'd query the DB using the dataSource
        return "User(" + userId + ")";
    }
}

class EmailService {
    public void sendEmail(String to, String message) {
        // In a real scenario, you'd use an SMTP server or API here.
        System.out.println("Sending email to " + to + ": " + message);
    }
}

class UserService {
    private final UserRepository userRepository;
    private final EmailService emailService;

    public UserService(UserRepository userRepository, EmailService emailService) {
        this.userRepository = userRepository;
        this.emailService = emailService;
    }

    public void performUserOperation(String userId) {
        String user = userRepository.findUserById(userId);
        // Maybe we do something complex, then send an email notification:
        emailService.sendEmail("admin@example.com", "Operation performed on " + user);
    }
}

class UserController {
    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    public void handleRequest(String userId) {
        // In a web app, this might be triggered by an HTTP request
        System.out.println("Handling request for user: " + userId);
        userService.performUserOperation(userId);
    }
}

// ======== Application Root (Manual Wiring) ========

public class App {
    public static void main(String[] args) {
        // Without a DI framework, we must carefully build the object graph:
        DataSource dataSource = new DataSource("jdbc:mysql://localhost:3306/mydb");
        UserRepository userRepository = new UserRepository(dataSource);
        EmailService emailService = new EmailService();
        UserService userService = new UserService(userRepository, emailService);
        UserController userController = new UserController(userService);

        // Now we can use the fully wired controller
        userController.handleRequest("42");
    }
}

```

# Practical DI in Spring (How)

Now that we learned the theory/motivation behind dependency injection and saw what manual dependency injection looks like, we now look at practical dependency injection in Spring. Frameworks like Spring actually automate the process of wiring objects and creating the application's object graph. We just need to introduce a few Spring annotations to our code and learn what beans are.
## What are Beans

Instead of having to wire all the objects yourself, frameworks like Spring will manage your objects and construct your object graph for you. All the objects managed by Spring are called "beans" and all beans are stored in a central object container called the "IoC container". Beans are allowed to reference other beans as dependencies. Spring will recursively resolve all bean dependencies and create the entire bean object graph for your application.  The actual algorithm for how this is done is very simple. It essentially just does a DFS traversal of your object graph and starts by creating objects that have no dependencies first and works its way up the tree.
## Creating Beans

There are 2 ways to create beans.
1. Mark a class with @Component/@Service/@Repository/@Controller (All equivalent). Any class marked with one of those annotations will be considered a bean and one instance of that class will be created and stored in the IoC container by Spring at the start of the app. And because any class marked with @Component is considered a bean, the class can then reference other beans it needs as dependencies inside its constructor and Spring will automatically resolve those beans from the IoC and pass it in. The constructor just needs to be marked with @Autowired. 
   
   Example:
```java
@Service
public class UserRepository {
    private final DatabaseConnection db;

    @Autowired
    public UserRepository(DatabaseConnection db) {
        this.db = db;
    }

    public getAllUsers() {
        return this.db.fetch("SELECT * FROM USERS;");
    }
}
```

2. The second way to create beans is to create a @Configuration class and insert @Bean factory methods that create the beans you want. A bean factory method is allowed to reference other beans in its function parameters. Spring will resolve any beans referenced in the function parameters of the bean factory method and pass them in when creating the bean. 
   
   Example of a simple config file with just 2 bean factory methods (dataSource and jdbcTemplate).
```java
@Configuration
public class ApplicationConfig {

    @Bean
    public DataSource dataSource() {
        return new DataSource("jdbc:mysql://localhost:3306/mydb");
    }

    @Bean
    public JdbcTemplate jdbcTemplate(DataSource dataSource) {
        return new SimpleJdbcTemplate(dataSource);
    }
}
```