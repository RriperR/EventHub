# GraphQL API

Примеры запросов:

### Создание события
```graphql
mutation {
  createEvent(data:{
    id:"e1",
    ts:"2025-01-01T10:00:00",
    type:"patient.created",
    tenantId:"t1",
    actorId:"u1",
    patientId:"p1",
    props:{ source:"test" }
  })
}
```

### Чтение событий
```graphql
query {
  events(limit:10) {
    id
    type
    ts
    tenantId
    actorId
    patientId
    props
  }
}
```
