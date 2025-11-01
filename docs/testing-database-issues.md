# Testing Database Issues and Solutions

This document explains two critical database-related issues we encountered while implementing authentication tests, and how we solved them.

---

## **Problem 1: Test Database Not Shared Across Connections**

### **The Problem**

When we first wrote tests for the auth API endpoints, they failed with:
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: users
```

But the weird thing was:
- The test fixture **did** call `Base.metadata.create_all(bind=engine)` to create tables
- We **did** override `get_db` dependency with `app.dependency_overrides[get_db] = override_get_db`
- The auth module tests (password hashing, JWT) all passed

### **Root Cause**

SQLite in-memory databases (`:memory:` or no file path) create a **separate database for each connection**. Here's what was happening:

1. Test fixture creates engine and connection #1 → Creates tables in database instance A
2. FastAPI endpoint opens connection #2 → Gets a **different** database instance B (no tables!)
3. Test fails because database B has no `users` table

### **The Fix**

```python
from sqlalchemy.pool import StaticPool

engine = create_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,  # ← This is the key!
    connect_args={"check_same_thread": False},
)
```

**What `StaticPool` does**: It ensures **all connections share the exact same database instance**. Think of it like everyone using the same workspace instead of each person getting their own isolated copy.

**Visual analogy**:
```
WITHOUT StaticPool:
  Connection 1 → Memory DB Instance A [has tables] ✅
  Connection 2 → Memory DB Instance B [empty] ❌
  Connection 3 → Memory DB Instance C [empty] ❌

WITH StaticPool:
  Connection 1 → Memory DB Instance A [has tables] ✅
  Connection 2 → Memory DB Instance A [has tables] ✅
  Connection 3 → Memory DB Instance A [has tables] ✅
```

**Location of fix**: `tests/test_auth_api.py` in the `client()` fixture

---

## **Problem 2: Dependency Injection Not Respecting Overrides**

### **The Problem**

After fixing problem #1, I tried to create `get_current_user_from_db()` dependency that needs database access. My first attempts failed because the dependency couldn't properly access the **test database**.

The issue: How do you make a dependency in `src/auth.py` use `get_db` when:
- Can't import `get_db` at module level (circular import: `auth.py` → `database.py` → potentially back)
- Need it to use the **overridden** `get_db` in tests, not the production one

### **Failed Attempts**

**Attempt 1: Manual database session**
```python
def get_current_user_from_db(credentials = Depends(security)):
    from src.database import SessionLocal
    db = SessionLocal()  # ❌ Creates production DB session, ignores test override!
```
**Problem**: `SessionLocal` always connects to production database, bypassing `app.dependency_overrides`.

**Attempt 2: Manually calling get_db()**
```python
def get_current_user_from_db(credentials = Depends(security)):
    from src.database import get_db
    db_gen = get_db()  # ❌ Calls production get_db, ignores override!
    db = next(db_gen)
```
**Problem**: `app.dependency_overrides` only works when **FastAPI's dependency injection system** calls the function, not when we call it manually.

### **The Root Cause**

FastAPI's `app.dependency_overrides` is like a lookup table:
```python
app.dependency_overrides = {
    get_db: override_get_db  # "When you need get_db, use override_get_db instead"
}
```

But this **only works when FastAPI resolves dependencies automatically**. When we manually call `get_db()` or use `SessionLocal()`, we bypass FastAPI entirely.

### **The Fix: Factory Pattern**

```python
def make_get_current_user_from_db() -> Any:
    """Factory function that creates the dependency."""
    from src.database import get_db  # ← Import inside function (avoids circular import)
    from src.models import User

    def get_current_user_from_db(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db),  # ← FastAPI will handle this dependency!
    ) -> Any:
        # Extract token, validate, query database...
        user = db.query(User).filter(User.id == user_id).first()
        return user

    return get_current_user_from_db

# Create the actual dependency
get_current_user_from_db = make_get_current_user_from_db()
```

**Why this works**:

1. **Factory function** (`make_get_current_user_from_db`) runs once at module load time
2. It imports `get_db` **inside** the function (avoiding circular import at module level)
3. Returns an inner function that has `db: Session = Depends(get_db)` as a parameter
4. When FastAPI sees `Depends(get_current_user_from_db)`, it:
   - Sees it needs a `db` parameter
   - Sees `Depends(get_db)`
   - Checks `app.dependency_overrides` → finds `override_get_db` in tests!
   - Calls `override_get_db()` to get the test database session ✅

**Visual flow in tests**:
```
Test calls endpoint
  ↓
FastAPI sees: current_user = Depends(get_current_user_from_db)
  ↓
FastAPI sees: get_current_user_from_db needs db = Depends(get_db)
  ↓
FastAPI checks: app.dependency_overrides[get_db] → found override_get_db!
  ↓
FastAPI calls: override_get_db() → returns test database session
  ↓
get_current_user_from_db receives test database session ✅
```

**Location of fix**: `src/auth.py` - the `make_get_current_user_from_db()` factory function

---

## **Key Lessons**

### **Problem 1 Lesson: SQLite In-Memory Database Isolation**
- SQLite in-memory databases are isolated per connection by default
- Use `StaticPool` in tests to share one database instance across all connections
- This is **only needed for testing** - production databases (PostgreSQL, etc.) don't have this issue
- Alternative: Use a file-based SQLite database for tests (slower but avoids this problem)

### **Problem 2 Lesson: FastAPI Dependency Injection**
- `app.dependency_overrides` only works when FastAPI resolves dependencies
- Manually calling functions bypasses dependency injection entirely
- Use factory pattern to delay imports and let FastAPI handle dependency resolution
- Never create database sessions manually in dependencies - always use `Depends()`
- The dependency injection system is **not just syntactic sugar** - it's a fundamental mechanism

### **The "Black in the Dal" Moments**

Both times I said "there's something black in the dal," it was because:

1. **Problem 1**: I was trying increasingly complex solutions (event listeners, model imports, different connection strings) when the real issue was SQLite's connection pooling behavior
2. **Problem 2**: I kept trying to work around dependency injection (calling functions manually, creating sessions directly) instead of working **with** it

**The lesson**: When a framework provides a mechanism (like dependency injection), use it properly rather than fighting against it!

---

## **General Testing Principles**

### **When Writing Tests for FastAPI Endpoints**

1. **Always use dependency overrides for external dependencies**:
   ```python
   app.dependency_overrides[get_db] = override_get_db
   app.dependency_overrides[get_current_user] = override_get_current_user
   ```

2. **For SQLite in-memory tests, always use StaticPool**:
   ```python
   engine = create_engine(
       "sqlite:///:memory:",
       poolclass=StaticPool,
       connect_args={"check_same_thread": False}
   )
   ```

3. **Import models before creating tables**:
   ```python
   from src.models import User, Game, GamePlayer  # Import all models
   Base.metadata.create_all(bind=engine)  # Now tables are created
   ```

4. **Clean up after tests**:
   ```python
   yield test_client  # Test runs here
   Base.metadata.drop_all(bind=engine)  # Cleanup
   app.dependency_overrides.clear()  # Reset overrides
   ```

### **When Writing Dependencies**

1. **Never manually create sessions in dependencies**:
   ```python
   # ❌ Bad - bypasses dependency injection
   def my_dependency():
       db = SessionLocal()
       # ...

   # ✅ Good - uses dependency injection
   def my_dependency(db: Session = Depends(get_db)):
       # ...
   ```

2. **Use factory pattern for circular import issues**:
   ```python
   def make_dependency():
       from some_module import needed_function  # Import inside factory

       def dependency(param = Depends(needed_function)):
           # Use param
           pass

       return dependency

   my_dependency = make_dependency()
   ```

3. **Trust FastAPI's dependency injection system**:
   - It handles caching within a request
   - It respects overrides in tests
   - It manages cleanup (for generators)
   - It resolves dependencies recursively

---

## **Debugging Tips**

### **If Tests Fail with "No Such Table"**

1. Check if you're using in-memory SQLite → Add `StaticPool`
2. Verify models are imported before `create_all()`
3. Add `echo=True` to engine to see SQL queries
4. Check that `app.dependency_overrides` is set correctly

### **If Dependency Overrides Don't Work**

1. Are you manually calling functions instead of using `Depends()`?
2. Are you creating sessions with `SessionLocal()` directly?
3. Are you using the same `app` instance in tests and implementation?
4. Did you clear overrides from a previous test?

### **General Debugging Strategy**

1. Add print statements or logging to see which database is being used
2. Check SQL logs (`echo=True`) to see where queries are going
3. Use debugger to step through dependency resolution
4. Test with a file-based SQLite database to rule out pooling issues

---

## **References**

- FastAPI Dependency Injection: https://fastapi.tiangolo.com/tutorial/dependencies/
- SQLAlchemy Connection Pooling: https://docs.sqlalchemy.org/en/20/core/pooling.html
- Testing FastAPI: https://fastapi.tiangolo.com/tutorial/testing/
- Our test fixtures: `tests/test_auth_api.py` (line 19-64)
- Our auth dependency: `src/auth.py` (line 182-245)

---

**Last Updated**: 2025-10-31 (Week 5 Day 3)
