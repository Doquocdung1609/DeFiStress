from __future__ import annotations

from typing import Any

from backend.app.adapters.graph import GraphClient, GraphError

USER_DEBT_QUERY = """
query DebtUsers(
  $block: Int!
  $first: Int!
  $skip: Int!
) {
  variableDebt: userReserves(
    block: { number: $block }
    first: $first
    skip: $skip
    orderBy: id
    orderDirection: asc
    where: {
      scaledVariableDebt_gt: "0"
    }
  ) {
    id
    user {
      id
    }
    scaledVariableDebt
    principalStableDebt
  }

  stableDebt: userReserves(
    block: { number: $block }
    first: $first
    skip: $skip
    orderBy: id
    orderDirection: asc
    where: {
      principalStableDebt_gt: "0"
    }
  ) {
    id
    user {
      id
    }
    scaledVariableDebt
    principalStableDebt
  }
}
"""

# The configured decentralized deployment currently exposes the Messari lending
# schema. Keep userReserves as the primary Aave-native query, but support that
# deployment by reading positive BORROWER positions when the entity is absent.
POSITION_DEBT_QUERY = """
query DebtPositions(
  $block: Int!
  $first: Int!
  $skip: Int!
) {
  positions(
    block: { number: $block }
    first: $first
    skip: $skip
    orderBy: id
    orderDirection: asc
    where: {
      side: BORROWER
      balance_gt: "0"
    }
  ) {
    id
    account {
      id
    }
    balance
    type
  }
}
"""


def discover_borrowers_from_graph(
    graph: GraphClient,
    *,
    block_number: int,
    page_size: int = 100,
    max_pages: int = 10,
    max_users: int = 500,
) -> list[str]:
    if page_size <= 0:
        raise ValueError("GRAPH_PAGE_SIZE must be positive")
    if max_pages <= 0:
        raise ValueError("GRAPH_MAX_PAGES must be positive")
    if max_users <= 0:
        return []

    try:
        return _discover_user_reserves(graph, block_number, page_size, max_pages, max_users)
    except GraphError as exc:
        if "has no field `userReserves`" not in str(exc):
            raise
        print("[GRAPH] userReserves unavailable; using positive BORROWER positions schema", flush=True)
        return _discover_positions(graph, block_number, page_size, max_pages, max_users)


def _discover_user_reserves(
    graph: GraphClient,
    block_number: int,
    page_size: int,
    max_pages: int,
    max_users: int,
) -> list[str]:
    users: set[str] = set()
    for page in range(max_pages):
        skip = page * page_size
        data = graph.query(
            USER_DEBT_QUERY,
            {
                "block": block_number,
                "first": page_size,
                "skip": skip,
            },
        )

        variable_rows = data.get("variableDebt", [])
        stable_rows = data.get("stableDebt", [])
        if not isinstance(variable_rows, list) or not isinstance(stable_rows, list):
            raise RuntimeError("The Graph returned an invalid userReserves payload")
        rows = [*variable_rows, *stable_rows]
        print(
            f"[GRAPH] page={page + 1} "
            f"variable={len(variable_rows)} "
            f"stable={len(stable_rows)}",
            flush=True,
        )
        for row in rows:
            if not isinstance(row, dict):
                raise RuntimeError("The Graph returned a non-object userReserve row")
            user = row.get("user")
            address = user.get("id") if isinstance(user, dict) else user
            result = _add_candidate(users, address, max_users)
            if result is not None:
                return result
        if (
            len(variable_rows) < page_size
            and len(stable_rows) < page_size
        ):
            break
    return _finish(users)


def _discover_positions(
    graph: GraphClient,
    block_number: int,
    page_size: int,
    max_pages: int,
    max_users: int,
) -> list[str]:
    users: set[str] = set()
    for page in range(max_pages):
        rows = graph.query(
            POSITION_DEBT_QUERY,
            {"block": block_number, "first": page_size, "skip": page * page_size},
        ).get("positions", [])
        if not isinstance(rows, list):
            raise RuntimeError("The Graph returned an invalid positions payload")
        print(f"[GRAPH] page={page + 1} positions={len(rows)}", flush=True)
        for row in rows:
            if not isinstance(row, dict):
                raise RuntimeError("The Graph returned a non-object position row")
            account = row.get("account")
            address = account.get("id") if isinstance(account, dict) else account
            result = _add_candidate(users, address, max_users)
            if result is not None:
                return result
        if len(rows) < page_size:
            break
    return _finish(users)


def _add_candidate(users: set[str], address: Any, max_users: int) -> list[str] | None:
    if isinstance(address, str) and address:
        users.add(address.lower())
    if len(users) < max_users:
        return None
    result = sorted(users)[:max_users]
    print(f"[GRAPH] Candidate borrowers: {len(result)}", flush=True)
    return result


def _finish(users: set[str]) -> list[str]:
    result = sorted(users)
    print(f"[GRAPH] Candidate borrowers: {len(result)}", flush=True)
    return result
