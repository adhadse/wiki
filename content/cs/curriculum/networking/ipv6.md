# IPv6

## Why IPv6?

The Internet Engineering Task Force ([IETF](https://en.wikipedia.org/wiki/Internet_Engineering_Task_Force)) created IPv4 (RFC 791) with an address space of 4.3 billion, initially believed to be sufficient for all devices connecting to the Internet. However, as early as the late 1980s, when the Internet began to flourish, experts foresaw the eventual [exhaustion of IPv4 addresses](https://en.wikipedia.org/wiki/IPv4_address_exhaustion).

## What is IPv6?

IPv6 is newer and better version of Internet Protocol bringing about 3.4\*10^38 total addresses and many provides other technical benefits such as hierarchical address allocation methods & multicast addressing is expanded and simplified. Do note that IPv4 and IPv6 are not interoperable.

## The IPv6 Address

Remember IPv4 address looks like this:

The bits refer to the binary digits of the address.

$$
\underbrace{192.168.32.152}_{\text{32-bit in length}}
$$

is made up four sections called _octets_, each octet can contain any number between 0-255:

<div>
$$
\underbrace{192}_{\text{octet}}.\underbrace{168}_{\text{octet}}.\underbrace{32}_{\text{octet}}.\underbrace{152}_{\text{octet}}
$$
</div>

Let's look at IPv6 address:

$$
\text{2001:0db8:0000:0000:a111:b222:c333:abcd}
$$

Things to note with IPv6:

1. In comparison to IPv4 which is 32 bits long, <mark class="y">IPv6 address is 128 bits long.</mark>
2. IPv4 has 4 sections calles _octets_, but <mark class="y">IPv6 has 8 sections called _hextets_.</mark>
3. IPv4 uses `.` to separate _octets_. <mark class="y">IPv6 uses `:` to separate hextets.</mark>

## IPv6 in Binary

IPv4 is usually represented in decimal format, but IPv6 is hexadecimal that is it is generally represented using any character between `0-9` and `a-f`.

Each hexadecimal character is made up of four binary bits which can be 0 or 1. Each bit represents a value of 1, 2, 4 or 8. It doubles with each column from right to left.

<div>
$$
\def\arraystretch{1.5}
   \begin{array}{c:c:c:c}
   8 & 4 & 2 & 1 \\ \hline
   0 & 0 & 0 & 0 \\
\end{array}
$$
</div>

Wherever we see a `1`, that toggles that column on, and wherever we see a `0` that toggles that column off.

We then add up all of the columns that have a 1 and this gives us our number or letter.

- To make the number `2` from our binary bits, we switch on the column for 2. Giving us the binary value for our first number: `0010`.
- To make the second number `0` from our binary bits, we keep all bits off.

<div>
$$
\underbrace{
  \textcolor{#07fc03}{2}
}_{\text{0010}}
\text{001:0db8:0000:0000:a111:b222:c333:abcd}

\newline

\def\arraystretch{1.5}
\begin{array}{c:c:c:c}
8 & 4 & 2 & 1 \\ \hline
0 & 0 & \textcolor{#f56c42}{1} & 0 \\
\end{array}
$$
</div>

<div>
$$
\text{2}
\underbrace{
  \textcolor{#07fc03}{0}
}_{\text{0000}}
\text{01:0db8:0000:0000:a111:b222:c333:abcd}

\newline

\def\arraystretch{1.5}
\begin{array}{c:c:c:c}
8 & 4 & 2 & 1 \\ \hline
0 & 0 & 0 & 0 \\
\end{array}
$$
</div>

For `d` (or any alphabet), it gets interesting. The hexadecimal digits ends at `f` like this:

<div>
$$

\def\arraystretch{1.5}
\begin{array}{}
1 & 2 & 3 & 4 & 5 & 6 & 7 & 8 & 9 & a & b & c & d & e & f \\
1 & 2 & 3 & 4 & 5 & 6 & 7 & 8 & 9 & 10 & 11 & 12 & 13 & 14 & 15 \\
\end{array}

$$
</div>

We should always start with the highest number you can in our original table in order to achieve our desired digit and in this case that number is `8`.

So, to achieve `13` or `d`, we'll try representing `13` in binary like this:

<div>
$$

\text{2001:0000:0}
\underbrace{
\textcolor{#07fc03}{d}
}_{\text{1101}}
\text{b8:0000:0000:a111:b222:c333:abcd}

\newline

\def\arraystretch{1.5}
\begin{array}{c:c:c:c}
8 & 4 & 2 & 1 \\ \hline
1 & 1 & 0 & 1 \\
\end{array}

$$
</div>

Continuing this we'll achieve this binary digits:

$$
10000000000001:110110111000:000000000000:000000000000:1010000100010001:1011001000100010:1100001100110011:1010101111001101
$$

## Network Section
Just like IPv4, IPv6 has network section.

<div>
$$
\underbrace{\textcolor{#ecf549}{2001}:\textcolor{#ecf549}{0db8}:\textcolor{#ecf549}{0000}:\textcolor{#ecf549}{0000}}_\text{Network section}:
\underbrace{a111:b222:c333:abcd}_\text{Host section}\textcolor{#ecf549}{/64}
$$
</div>

IPv4 uses subnet mask to define this network section, <mark class="y">however IPv6 gets rid of subnet mask</mark> and <mark class="v"> instead it just uses a `/` and number of network bits.</mark>

In above example $\textcolor{#ecf549}{64}$ is half of our 128 bit address. `/64` addresses are common when it comes to IPv6.

## Compressing the Address
1. The first trick is to <mark class="y">remove continuous zeroes and replace it with **double colon**</mark>, computer can then figure out <mark class="y">there are two missing hextets</mark> and then it fill it up with zeroes.

    - <mark class="r">The rule to this is it can only appear once.</mark>

    $$
    \text{2001:0db8:\underline{0000:0000}:a111:b222:c333:abcd}
    \newline
    \text{2001:0db8\textcolor{#ecf549}{::}a111:b222:c333:abcd}
    $$

    So, this **we cannot do!**

    $$
    \text{2001:0db8:\underline{0000:0000}:a111:b222:0000:abcd}
    \newline
    \text{2001:0db8\textcolor{#ecf549}{::}a111:b222\textcolor{#ecf549}{::}abcd}
    $$

2. Second trick, <mark class="y">we can all leading zeroes from each hextets and remove them</mark>:

    $$
    \text{2001:\textcolor{#ecf549}{0}db8\textcolor{#ecf549}{::}a111:b222:\textcolor{#ecf549}{000}0:abcd}
    \newline
    \text{2001:db8\textcolor{#ecf549}{::}a111:b222:0:abcd}
    $$

    - We need to leave last `0` is second last hextet since we already placed `::`.

## Global Unicast address
Just like IPv4 there are different type of IPv6 addresses and they serve different purposes.

This one is <mark class="v">Global unicast address</mark>, unlike IPv4, we don't need to rely on private addresses. Every device can have it's own public IP addresses.

$$
\underbrace{
  \textcolor{#ecf549}{2001:0db8:0000}
}_{\text{Global Prefix}}
\text{:0000:a111:b222:c333:abcd}
$$

The first part of IPv6 Global prefix is called <mark class="v"> atleast 48 bits long *Global Prefix*</mark> which is provided by your ISP (Internet service provider).

After Global prefix, we use the next <mark class="v">16-bits for *subnet IDs*</mark>.

  - <mark class="y">16 bits give us over 65,000 subnets to play with</mark>

<div>
$$
\underbrace{
  \textcolor{#ecf549}{2001:0db8:0000}
}_{\text{Global Prefix}}:
\overbrace{
  \textcolor{#07fc03}{0000}
}^{\text{Subnet ID}}
\text{:a111:b222:c333:abcd}
$$
</div>

The remaining <mark class="v">48-bits can then be used for host or interface ID</mark>

<div>
$$
\underbrace{
  \textcolor{#ecf549}{2001:0db8:0000}
}_{\text{Global Prefix}}:
\overbrace{
  \textcolor{#07fc03}{0000}
}^{\text{Subnet ID}}:
\underbrace{
  \text{a111:b222:c333:abcd}
}_{\text{Interface ID}}:
$$
</div>

## Other address type

|Address type    |          |                        |
|----------------| ---------| -----------------------|
| Global unicast | `2000::/3` | Publicly routable      |
| Unique local   | `fc00::/7` | Routable in the LAN    |
| Link local     | `fe80::/10`  | Not routable         |
| Multicast      | `ff00::/8`   | Addresses for groups |
| Anycast        | `2000::/3`     | Shared address     |

1. **Global Unicast** (`2000::/3`): The prefix to identify these address is like `2000::/3` which means, <mark class="y">the `/3` first three bits identify a global unicast address are fixed. It will start with either a 2 or a 3</mark>

    - i.e. the address will lie in range `2000::/3` to `3fff::/3`. And in binary notation, <mark class="y">the first 3 bits will remain contant</mark>
      - addresses in `2000::` to `3fff:ffff:fff1f:ffff:ffff:ffff:ffff:ffff`
      - So in binary addresses starting with

        $$
        \textcolor{#07fc03}{0010}{000000000000}:0000000000000000:0000000000000000:0000000000000000:0000000000000000:0000000000000000:0000000000000000:0000000000000000
        $$

        to address:

        $$
        \textcolor{#07fc03}{0011}{111111111111}:1111111111111111:1111111111111111:1111111111111111:1111111111111111:1111111111111111:1111111111111111:1111111111111111
        $$

    - Globally unique and routable, similar to public IPv4 address.

2. **Unique local** (`fc00::/7`): These are like IPv4 private address, not gloabally routable but routable only within the scope of private networks.

    - Unique local address will always start with `f` followed by either `c` or a `d`
    - Unique local addresses may be used freely, without centralized registration, inside a signle site or organization.

3. **Link local** (`fe80::/10`): Link-local addresses allow communication between neighboring nodes without needing a globally unique address. IPv6 routers do not forward data with link-local addresses beyond the local network. All IPv6-enabled interfaces automatically have a link-local unicast address.

  - Think of this as similar to `169.254.xxx.xxx` of IPv4.
  - Are crucial for tasks like automatic address configuration and for the Neighbor Discovery Protocl (NDP), which help devices on the same link find and communicate with each other.

4. **Mulicast** (`ff00::/8`): These addresses are sent to a group of nodes listening for that particular multicast address.

  - IPv6 abolishes IPv4 broadcast communication completely, replacing it with IPv6 multicast, implemented using Protocol Independent Multicast (PIM) routing.

5. **Anycast** (`2000::/3`): IPv6 allows us to assign the same IP address to multiple devices. The data is then sent to the closest device with that address. There isn't a specific range for anycast address, they use the same address space as global unicast address.
