# Jest

## Globals

### `afterAll(fn, timeout)`

- It runs a function after all the tests in this file have completed.

### `afterEach(fn, timeout)`

- It runs a function after each one of the tests in this file completes.

```js
afterEach(() => { // for the previous: afterAll(() => {
    cleanUpDatabase(globalDatabase);
});
```

### `beforeAll(fn, timeout)`

- It runs a function before any of the tests in this file run.

```js
```

### `beforeEach(fn, timeout)`

```js
beforeEach(() => { // for the previous: beforeAll(() => {
    return globalDatabase.clear().then(() => {
        return globalDatabase.insert({data: 'foo'});
    });
});
```

### `describe(name, fn)`

- It creates a block that groups together several related tests.

```js
const myBeverage = {
  delicious: true,
  sour: false,
};

describe('my beverage', () => {
  test('is delicious', () => {
    expect(myBeverage.delicious).toBeTruthy();
  });

  test('is not sour', () => {
    expect(myBeverage.sour).toBeFalsy();
  });
});
```

### `describe.each(table)(name, fn, timeout)`

- Use it if you keep duplicating the same test suites with different data.

```js
describe.each([
  [1, 1, 2],
  [1, 2, 3],
  [2, 1, 3],
])('.add(%i, %i)', (a, b, expected) => {
  test(`returns ${expected}`, () => {
    expect(a + b).toBe(expected);
  });

  test(`returned value not be greater than ${expected}`, () => {
    expect(a + b).not.toBeGreaterThan(expected);
  });

  test(`returned value not be less than ${expected}`, () => {
    expect(a + b).not.toBeLessThan(expected);
  });
});
```

### `describe.only(name, fn)`

- If you want to run only one describe block.

```js
describe.only('my beverage', () => {
  test('is delicious', () => {
    expect(myBeverage.delicious).toBeTruthy();
  });

  test('is not sour', () => {
    expect(myBeverage.sour).toBeFalsy();
  });
});

describe('my other beverage', () => {
  // ... will be skipped
});
```

### `describe.only.each(table)(name, fn)`

- If you want to only run specific tests suites of data driven tests.

```js
describe.only.each([
  [1, 1, 2],
  [1, 2, 3],
  [2, 1, 3],
])('.add(%i, %i)', (a, b, expected) => {
  test(`returns ${expected}`, () => {
    expect(a + b).toBe(expected);
  });
});

test('will not be run', () => {
  expect(1 / 0).toBe(Infinity);
});
```

### `describe.skip(name, fn)`

- If you do not want to run the tests of a particular `describe` block.

```js
describe('my beverage', () => {
  test('is delicious', () => {
    expect(myBeverage.delicious).toBeTruthy();
  });

  test('is not sour', () => {
    expect(myBeverage.sour).toBeFalsy();
  });
});

describe.skip('my other beverage', () => {
  // ... will be skipped
});
```

### `describe.skip.each`

- If you want to stop running a suite of data driven tests.

```js
describe.skip.each([
  [1, 1, 2],
  [1, 2, 3],
  [2, 1, 3],
])('.add(%i, %i)', (a, b, expected) => {
  test(`returns ${expected}`, () => {
    expect(a + b).toBe(expected); // will not be run
  });
});

test('will be run', () => {
  expect(1 / 0).toBe(Infinity);
});
```

### `test(name, fn, timeout)`

```js
test('has lemon in it', () => {
  return fetchBeverageList().then(list => {
    expect(list).toContain('lemon');
  });
});
```

### `test.concurrent(name, fn, timeout)`

- If you want the test to run concurrently.

```js
test.concurrent('addition of 2 numbers', async () => {
  expect(5 + 3).toBe(8);
});

test.concurrent('subtraction 2 numbers', async () => {
  expect(5 - 3).toBe(2);
});
```

### `test.concurrent.each(table)(name, fn, timeout)`

- If you keep duplicating the same test with different data.

```js
test.concurrent.each([
  [1, 1, 2],
  [1, 2, 3],
  [2, 1, 3],
])('.add(%i, %i)', async (a, b, expected) => {
  expect(a + b).toBe(expected);
});
```

### `test.concurrently.only.each(table)(name, fn)`

- If you want to only run specific tests with different test data concurrently.

```js
test.concurrent.only.each([
  [1, 1, 2],
  [1, 2, 3],
  [2, 1, 3],
])('.add(%i, %i)', async (a, b, expected) => {
  expect(a + b).toBe(expected);
});

test('will not be run', () => {
  expect(1 / 0).toBe(Infinity);
});
```

### `test.concurrent.skip.each(table)(name, fn)`

- If you want to stop running a collection of asynchronous data driven tests.

```js
test.concurrent.skip.each([
  [1, 1, 2],
  [1, 2, 3],
  [2, 1, 3],
])('.add(%i, %i)', async (a, b, expected) => {
  expect(a + b).toBe(expected); // will not be run
});

test('will be run', () => {
  expect(1 / 0).toBe(Infinity);
});
```

### `test.each(table)(name, fn, timeout)`

- If you keep duplicating the same test with different data.

```js
test.each([
  [1, 1, 2],
  [1, 2, 3],
  [2, 1, 3],
])('.add(%i, %i)', (a, b, expected) => {
  expect(a + b).toBe(expected);
});
```

### `test.failing(name, fn, timeout)`

- When you are writing a test and expecting it to fail.

```js
test.failing('it is not equal', () => {
  expect(5).toBe(6); // this test will pass
});

test.failing('it is equal', () => {
  expect(10).toBe(10); // this test will fail
});
```

### `test.failing.each(name, fn, timeout)`

### `test.only.failing(name, fn, timeout)`

### `test.skip.failing(name, fn, timeout)`

### `test.only(name, fn, timeout)`

### `test.only.each(table)(name, fn)`

### `test.skip(name, fn)`

### `test.skip.each(table)(name, fn)`

### `test.todo(name)`

- When you are planning on writing tests.

## Expect

### `expect(value)`

```js
test('the best flavor is grapefruit', () => {
  expect(bestLaCroixFlavor()).toBe('grapefruit');
});
```

### `.not`

```js
test('the best flavor is not coconut', () => {
  expect(bestLaCroixFlavor()).not.toBe('coconut');
});
```

### `.resolves`

```js
test('resolves to lemon', () => {
  return expect(Promise.resolve('lemon')).resolves.toBe('lemon');
});
// OR
test('resolves to lemon', async () => {
  await expect(Promise.resolve('lemon')).resolves.toBe('lemon');
});
```

### `.rejects`

- It unwraps the reason of a rejected promise so any other matcher can be chained.

```js
test('rejects to octopus', () => {
  return expect(Promise.reject(new Error('octopus'))).rejects.toThrow(
    'octopus',
  );
});
```

### `.toBe(value)`

### `.toHaveBeenCalled()`

### `.toHaveBeenCalledTimes(number)`

```js
function drinkAll(callback, flavour) {
    if(flavour !== 'octopus') {
        callback(flavour);
    }
}

describe('drinkAll', () => {
    test('drinks something lemon-flavoured', () => {
        const drink = jest.fn();
        drinkAll(drink, 'lemon');
        expect(drink).toHaveBeenCalled();
    });
});
```

### `.toHaveBeenCalledWith(arg1, arg2, ...)`

```js
test('registration applies correctly to orange La Croix', () => {
   const beverage = new LaCroix('orange');
   register(beverage);
   const f = jest.fn();
   applyToAll(f);
   expect(f).toHaveBeenCalledWith(beverage); 
});
```

### `.toHaveBeenLastCalledWith(arg1, arg2, ...)`

### `.toHaveBeenNthCalledWith(nthCall, arg1, arg2, ...)`

```js
test('drinkEach drinks each drink', () => {
  const drink = jest.fn();
  drinkEach(drink, ['lemon', 'octopus']);
  expect(drink).toHaveBeenNthCalledWith(1, 'lemon');
  expect(drink).toHaveBeenNthCalledWith(2, 'octopus');
});
```

### `.toHaveReturned()`

- If you have a mock function, you can use .toHaveReturned to test that the mock function successfully returned (i.e., did not throw an error) at least one time.

```js
test('drinks returns', () => {
  const drink = jest.fn(() => true);
  drink();
  expect(drink).toHaveReturned();
});
```

### `.toHaveReturnedTimes(number)`

- It ensures that a mock function returned successfully an exact number of times.

```js
test('drink returns twice', () => {
    const drink = jest.fn(() => true);
    drink();
    drink();
    expect(drink).toHaveReturnedTimes(2);
});
```

### `.toHaveReturnedWith(value)`

- It ensures that a mock function returned a specific value.

```js
test('drink returns La Croix', () => {
  const beverage = {name: 'La Croix'};
  const drink = jest.fn(beverage => beverage.name);

  drink(beverage);

  expect(drink).toHaveReturnedWith('La Croix');
});
```

### `.toHaveLastReturnedWith(value)`

```js
test('drink returns La Croix (Orange) last', () => {
  const beverage1 = {name: 'La Croix (Lemon)'};
  const beverage2 = {name: 'La Croix (Orange)'};
  const drink = jest.fn(beverage => beverage.name);

  drink(beverage1);
  drink(beverage2);

  expect(drink).toHaveLastReturnedWith('La Croix (Orange)');
});
```

### `.toHaveNthReturnedWith(nthCall, value)`

```js
test('drink returns expected nth calls', () => {
  const beverage1 = {name: 'La Croix (Lemon)'};
  const beverage2 = {name: 'La Croix (Orange)'};
  const drink = jest.fn(beverage => beverage.name);

  drink(beverage1);
  drink(beverage2);

  expect(drink).toHaveNthReturnedWith(1, 'La Croix (Lemon)');
  expect(drink).toHaveNthReturnedWith(2, 'La Croix (Orange)');
});
```

### `toHaveLength(number)`

```js
expect([1, 2, 3]).toHaveLength(3);
```

### `.toHaveProperty(keyPath, value?)`

```js
const houseForSale = {
  bath: true,
  bedrooms: 4,
  kitchen: {
    amenities: ['oven', 'stove', 'washer'],
    area: 20,
    wallColor: 'white',
    'nice.oven': true,
  },
  livingroom: {
    amenities: [
      {
        couch: [
          ['large', {dimensions: [20, 20]}],
          ['small', {dimensions: [10, 10]}],
        ],
      },
    ],
  },
  'ceiling.height': 2,
};

test('this house has my desired features', () => {
  // Example Referencing
  expect(houseForSale).toHaveProperty('bath');
  expect(houseForSale).toHaveProperty('bedrooms', 4);

  expect(houseForSale).not.toHaveProperty('pool');

  // Deep referencing using dot notation
  expect(houseForSale).toHaveProperty('kitchen.area', 20);
  expect(houseForSale).toHaveProperty('kitchen.amenities', [
    'oven',
    'stove',
    'washer',
  ]);

  expect(houseForSale).not.toHaveProperty('kitchen.open');

  // Deep referencing using an array containing the keyPath
  expect(houseForSale).toHaveProperty(['kitchen', 'area'], 20);
  expect(houseForSale).toHaveProperty(
    ['kitchen', 'amenities'],
    ['oven', 'stove', 'washer'],
  );
  expect(houseForSale).toHaveProperty(['kitchen', 'amenities', 0], 'oven');
  expect(houseForSale).toHaveProperty(
    'livingroom.amenities[0].couch[0][1].dimensions[0]',
    20,
  );
  expect(houseForSale).toHaveProperty(['kitchen', 'nice.oven']);
  expect(houseForSale).not.toHaveProperty(['kitchen', 'open']);

  // Referencing keys with dot in the key itself
  expect(houseForSale).toHaveProperty(['ceiling.height'], 'tall');
});
```

### `.toBeCloseTo(number, numDigits?)`

- It compares floating point numbers for approximate equality.

```js
test('adding works sanely with decimals', () => {
  expect(0.2 + 0.1).toBe(0.3); // Fails!
});
```

### `.toBeDefined()`

- It checks that a variable is not undefined.

```js
test('there is a new flavor idea', () => {
  expect(fetchNewFlavorIdea()).toBeDefined();
});
```

### `.toBeFalsy()`

```js
drinkSomeLaCroix();
if(!getErrors()) {
    drinkMoreLaCroix();
}

test('drinking La Croix does not lead to errors', () => {
  drinkSomeLaCroix();
  expect(getErrors()).toBeFalsy();
});
```

### `.toBeGreaterThan(number | bigint)`

### `.toBeGreatedThanOrEqual(number | bigint)`

### `.toBeLessThan(number | bigint)`

### `.toBeLessThanOrEqual(number | bigint)`

### `.toBeInstanceOf(Class)`

### `.toBeNull()`

### `.toBeTruthy()`

### `.toBeUndefined()`

### `.toBeNaN()`

### `.toContain(item)`

```js
test('the flavor list contains lime', () => {
  expect(getAllFlavors()).toContain('lime');
});
```

### `.toContainEqual(item)`

```js
describe('my beverage', () => {
  test('is delicious and not sour', () => {
    const myBeverage = {delicious: true, sour: false};
    expect(myBeverages()).toContainEqual(myBeverage);
  });
});
```

### `.toEqual(value)`

### `.toMatch(regexp | string)`

```js
describe('an essay on the best flavor', () => {
  test('mentions grapefruit', () => {
    expect(essayOnTheBestFlavor()).toMatch(/grapefruit/);
    expect(essayOnTheBestFlavor()).toMatch(new RegExp('grapefruit'));
  });
});
```

### `.toMatchObject(object)`

```js
const houseForSale = {
  bath: true,
  bedrooms: 4,
  kitchen: {
    amenities: ['oven', 'stove', 'washer'],
    area: 20,
    wallColor: 'white',
  },
};
const desiredHouse = {
  bath: true,
  kitchen: {
    amenities: ['oven', 'stove', 'washer'],
    wallColor: expect.stringMatching(/white|yellow/),
  },
};

test('the house has my desired features', () => {
  expect(houseForSale).toMatchObject(desiredHouse);
});
```

### `.toMatchSnapshot(propertyMatchers?, hint?)`

### `.toMatchInlineSnapshot(propertyMatchers?, inlineSnapshot)`

### `.toStrictEqual(value)`

### `.toThrow(error?)`

- It tests that a function throws when it is called.

```js
test('throws on octopus', () => {
  expect(() => {
    drinkFlavor('octopus');
  }).toThrow();
});
```

### `.toThrowErrorMatchingSnapshot(hint?)`

### `.toThrowErrorMatchingInlineSnapshot(inlineSnapshot)`

### `expect.anything()`

- It matches anything but `null` or `undefined`.

```js
test('map calls its argument with a non-null argument', () => {
  const mock = jest.fn();
  [1].map(x => mock(x));
  expect(mock).toHaveBeenCalledWith(expect.anything());
});
```

### `expect.any(constructor)`

- It matches anything that was created with the given constructor or if it's a primitive that is of the passed type.

```js
class Cat {}
function getCat(fn) {
  return fn(new Cat());
}

test('randocall calls its callback with a class instance', () => {
  const mock = jest.fn();
  getCat(mock);
  expect(mock).toHaveBeenCalledWith(expect.any(Cat));
});
```

### `expect.arrayContaining(array)`

- It matches a received array which contains all of the elements in the expected array.

```js
describe('arrayContaining', () => {
    const expected = ['Alice', 'Bob'];
    it('matches even if received contains additional elements', () => {
        expect(['Alice', 'Bob', 'Eve']).toEqual(expect.arrayContaining(expected));
    })
});
```

### `expect.not.arrayContaining(array)`

### `expect.closeTo(number, numDigits?)`

```js
test('compare float in object properties', () => {
  expect({
    title: '0.1 + 0.2',
    sum: 0.1 + 0.2,
  }).toEqual({
    title: '0.1 + 0.2',
    sum: expect.closeTo(0.3, 5), // with a precision of 5 digits
  });
});
```

### `expect.objectContaining(object)`

```js
test('onPress gets called with the right thing', () => {
  const onPress = jest.fn();
  simulatePresses(onPress);
  expect(onPress).toHaveBeenCalledWith(
    expect.objectContaining({
      x: expect.any(Number),
      y: expect.any(Number),
    }),
  );
});
```

### `expect.not.objectContaining(object)`

### `expect.stringContaining(string)`

### `expect.not.stringContaining(string)`

### `expect.stringMatching(string | regexp)`

### `expect.not.stringMatching(string | regexp)`

### `expect.assertions(number)`

- It verifies that a certain number of assertions are called during a test.

```js
test('doAsync calls both callbacks', () => {
  expect.assertions(2);
  function callback1(data) {
    expect(data).toBeTruthy();
  }
  function callback2(data) {
    expect(data).toBeTruthy();
  }
  doAsync(callback1, callback2);
});
```

### `expect.hasAssertions()`

- It verifies that at least one assertion is called during a test.

```js
test('prepareState prepares a valid state', () => {
  expect.hasAssertions();
  prepareState(state => {
    expect(validateState(state)).toBeTruthy();
  });
  return waitOnState();
});
```

### `expect.addEqualityTesters(testers)`

- It adds your own methods to test if two objects are equal.

### `expect.addSnapshotSerializer(serializer)`

### `expect.extend(matchers)`

## Mock functions

- Mock functions are also known as _spies_.

### `mockFn.mockImplementation(fn)`

```js
const mockFn = jest.fn(scalar => 42 + scalar);

mockFn(0); // 42
mockFn(1); // 43
```

### `mockFn.mockImplementationOnce(fn)`

```js
const mockFn = jest
  .fn(() => 'default')
  .mockImplementationOnce(() => 'first call')
  .mockImplementationOnce(() => 'second call');

mockFn(); // 'first call'
mockFn(); // 'second call'
mockFn(); // 'default'
mockFn(); // 'default'
```

### `mockFn.mockReturnValue(value)`

```js
const mock = jest.fn();

mock.mockReturnValue(42);
mock(); // 42
```

- Shorthand for:

```js
jest.fn().mockImplementation(() => value);
```

### `mockFn.mockReturnValueOnce(value)`

```js
const mockFn = jest
  .fn()
  .mockReturnValue('default')
  .mockReturnValueOnce('first call')
  .mockReturnValueOnce('second call');

mockFn(); // 'first call'
mockFn(); // 'second call'
mockFn(); // 'default'
mockFn(); // 'default'
```

### `mockFn.mockResolvedValue(value)`

```js
jest.fn().mockImplementation(() => Promise.resolve(value));
```

```js
test('async test', async () => {
  const asyncMock = jest.fn().mockResolvedValue(43);
  await asyncMock(); // 43
});
```

### `mockFn.mockResolvedValueOnce(value)`

### `mockFn.mockRejectedValue(value)`

```js
jest.fn().mockImplementation(() => Promise.reject(value));
```

```js
test('async test', async () => {
  const asyncMock = jest
    .fn()
    .mockRejectedValue(new Error('Async error message'));
  await asyncMock(); // throws 'Async error message'
});
```

### `mockFn.mockRejectedValueOnce(value)`

### `mockFn.withImplementation(fn, callback)`

```js
test('test', () => {
  const mock = jest.fn(() => 'outside callback');
  mock.withImplementation(
    () => 'inside callback',
    () => {
      mock(); // 'inside callback'
    },
  );
  mock(); // 'outside callback'
});
```

## The jest object

### `jest.mock()`

```js
jest.mock('../moduleName', () => {
  return jest.fn(() => 42);
});

// This runs the function specified as second argument to `jest.mock`.
const moduleName = require('../moduleName');
moduleName(); // Will return '42';
```

### `jest.fn(implementation?)`

- It returns a new, unused mock function.

```js
const mockFn = jest.fn();
mockFn();
expect(mockFn).toHaveBeenCalled();

// with a mock implementation
const returnsTrue = jest.fn(() => true);
console.log(returnsTrue());
```

### `jest.spyOn(object, methodName)`

- It creates a mock function similar to `jest.fn`, but it also tracks calls to `object[methodName]`.
- It returns a jest mock function.

```js
const video = {
  play() {
    return true;
  },
};

module.exports = video;

// example test
const video = require('./video');

afterEach(() => {
  // restore the spy created with spyOn
  jest.restoreAllMocks();
});

test('plays video', () => {
  const spy = jest.spyOn(video, 'play');
  const isPlaying = video.play();

  expect(spy).toHaveBeenCalled();
  expect(isPlaying).toBe(true);
});
```

---

// test("playground", () => {
//   const mockFunction = jest.fn();
//   console.log("mockFunction", mockFunction);

//   axios.get = jest.fn();
//   console.log("mock Implementation:", axios.get.toString());

//   console.log("original Implementation:", Math.random.toString());
//   Math.random = jest.fn();
//   console.log("mock Implementation:", Math.random.toString());

//   // mock.calls lists function's args
//   // mocks.results lists the args results return throw incomplete
//   // mock.instances lists constructors products
//   // mock.contexts lists this objects
//   // mock.lastCall lists function's last call's args

//   function manipulateArray(array, manipulateMethod) {
//     return array.map((item) => manipulateMethod(item));
//   }
//   test("playground", () => {
//     const array = [0, 1, 2];
//     const mockManipulateMethod = jest.fn((x) => x + 2);
//     manipulateArray(array, mockManipulateMethod);
//     console.log("mock property:", mockManipulateMethod.mock);
//   });
// });
// test("playground", () => {
//   const mockFunction = jest
//     .fn()
//     .mockReturnValue("other calls")
//     .mockReturnValueOnce("first call")
//     .mockReturnValueOnce("second call");

//     for (let index = 0; index < 5; index++) {
//       console.log("mockedProduct", mockFunction());
//     }
// });
// });

//   function getFromLocalStorage(key) {
//     return window.localStorage.getItem(key);
//   }
//   test("should get data from local storage correctly", () => {
//     const key = "testKey";
//     const value = "testValue";
//     const mockLocalStorageGet = jest.fn();
//     Object.defineProperty(window, "localStorage", {
//       value: {
//         getItem: mockLocalStorageGet,
//       },
//     });
//     mockLocalStorageGet.mockReturnValue(value);
//     getFromLocalStorage(key);
//     expect(jest.isMockFunction(window.localStorage.getItem)).toBe(true);
//     expect(mockLocalStorageGet.mock.lastCall[0]).toBe(key);
//     expect(mockLocalStorageGet.mock.results[0].value).toBe(value);
// });

// function getRemainingTime(endDate, startDate=new Date()) {
//   let delta = (endDate - startDate) / 1000;

//   return {
//     remainingDays: Math.floor(delta / (60 * 60 * 24)),
//     remainingHours: Math.floor((delta / (60 * 60)) % 24),
//     remainingMinutes: Math.floor((delta / 60) % 60),
//     remainingSeconds: Math.floor(delta % 60),
//   };
// }

// test("should return remaining data given future date", () => {
//   const endDate = new Date(2023, 1, 1);

//   const mockCurrDate = new Date(2022, 10, 16, 16, 9, 25);

//   global.Date = jest.fn().mockReturnValue(mockCurrDate);

//   expect(getRemainingTime(endDate)).toEqual({
//     remainingDays: 76,
//     remainingHours: 7,
//     remainingMinutes: 50,
//     remainingSeconds: 35,
//   });
// });

// function manipulateArray(array, manipulateMethod) {
//   return array.map((item) => manipulateMethod(item));
// }

// test("playground", () => {
//   const array = [0, 1, 2];
//   const manipulateMethod = jest.fn().mockImplementation((x) => x + 2);
//   manipulateArray(array, manipulateMethod);

//   console.log(manipulateMethod.mock.results);
// });

// Mocking an asynchronous function
jest.fn().mockImplementation(() => Promise.resolve(value));
jest.fn().mockImplementation(() => Promise.reject(value));

// mockResolvedValue(value);
// mockResolvedValueOnce(value);
// mockRejectedValue(value);
// mockRejectedValueOnce(value);
